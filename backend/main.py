from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import json
import os
import re
from threading import Lock
from typing import Any, Dict, List
from urllib.error import URLError
from urllib.request import urlopen

from dotenv import load_dotenv
from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import JSONResponse, PlainTextResponse
import requests
from requests.exceptions import RequestException
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client
from twilio.twiml.voice_response import Gather, VoiceResponse


load_dotenv()


PHONE_PATTERN = re.compile(r"^\+91\d{10}$")
LANGUAGE_MENU_TIMEOUT_SECONDS = 10
LANGUAGE_REPROMPT_WAIT_SECONDS = 5
QUESTION_GATHER_TIMEOUT_SECONDS = 12
SPEECH_PRE_PROMPT_PAUSE_SECONDS = 1
TTS_VOICE = os.getenv("TWILIO_TTS_VOICE", "alice").strip() or "alice"
ENV_FILE_PATH = Path(__file__).resolve().parents[1] / ".env"
ENV_UPDATE_LOCK = Lock()


@dataclass(frozen=True)
class LanguagePack:
    name: str
    code: str
    confirmation: str
    close: str
    questions: Dict[int, str]


LANGUAGES: Dict[str, LanguagePack] = {
    "1": LanguagePack(
        name="English",
        code="en-IN",
        confirmation="Thank you. I will now speak in English. Let us begin.",
        close="Thank you. Have a great day. Goodbye.",
        questions={
            1: "How are you feeling right now?",
            2: "Is there any pain, dizziness, or discomfort right now?",
            3: "Did you take your morning medicines today?",
            4: "Can you tell me what you ate today?",
        },
    ),
    "2": LanguagePack(
        name="Hindi",
        code="hi-IN",
        confirmation="Dhanyavaad. Ab main Hindi mein baat karungi. Chaliye shuru karte hain.",
        close="Dhanyavaad. Apna khayal rakhein. Alvida.",
        questions={
            1: "Aap abhi kaisa mehsoos kar rahe hain?",
            2: "Kya abhi dard, chakkar, ya koi takleef hai?",
            3: "Kya aapne subah ki dawai le li thi?",
            4: "Aaj aapne kya khaya?",
        },
    ),
    "3": LanguagePack(
        name="Kannada",
        code="kn-IN",
        confirmation="Dhanyavadagalu. Iga nanu Kannada dalli matanaduttene. Prarambha madona.",
        close="Dhanyavadagalu. Chennagiri. Namaskara.",
        questions={
            1: "Neevu iga hegiddiri?",
            2: "Iga yavadadaru novvu, tale suttu, athava aswasthate ideya?",
            3: "Beliggeya aushadhi tegedukondiddira?",
            4: "Ivattu neevu enu tinniri?",
        },
    ),
    "4": LanguagePack(
        name="Tamil",
        code="ta-IN",
        confirmation="Nandri. Ippodu naan Tamil-la pesuven. Aarambikkalaam.",
        close="Nandri. Nalam irungal. Vanakkam.",
        questions={
            1: "Neenga ippo eppadi unarareenga?",
            2: "Ippo vali, thalai suttral, illatti yedhavadhu asaukarayam irukka?",
            3: "Kalaila marundhu eduthuteengala?",
            4: "Innikki neenga enna saaptenga?",
        },
    ),
    "5": LanguagePack(
        name="Telugu",
        code="te-IN",
        confirmation="Dhanyavaadalu. Ippudu nenu Telugu lo maatladutanu. Modalupeddaam.",
        close="Dhanyavaadaalu. Bagundu undandi. Namaskaram.",
        questions={
            1: "Meeru ippudu ela anipistondi?",
            2: "Ippudu meeku noppi, talatiruguta, leka asaukaryam unda?",
            3: "Meeru udayam mandulu teesukunnara?",
            4: "E roju meeru emi tinnaru?",
        },
    ),
    "6": LanguagePack(
        name="Marathi",
        code="mr-IN",
        confirmation="Dhanyavaad. Ata mi Marathi madhe bolen. Chala suru karuya.",
        close="Dhanyavaad. Khayal ghya. Namaskar.",
        questions={
            1: "Tumhala atta kase watat aahe?",
            2: "Atta dukhane, chakkar, kiwa kahi traas aahe ka?",
            3: "Tumhi sakalchi aushadhe ghetli ka?",
            4: "Aaj tumhi kay khalla?",
        },
    ),
}


@dataclass
class CallSession:
    call_id: str
    phone_number: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    language_digit: str = "1"
    language_chosen: str = "English"
    language_code: str = "en-IN"
    responses: Dict[str, str] = field(default_factory=dict)


@dataclass
class VapiCallSession:
    call_id: str
    phone_number: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    assistant_id: str = ""
    phone_number_id: str = ""
    status: str = "queued"
    transcripts: List[str] = field(default_factory=list)
    events: List[Dict[str, Any]] = field(default_factory=list)
    end_report: Dict[str, Any] = field(default_factory=dict)


ACTIVE_CALLS: Dict[str, CallSession] = {}
VAPI_ACTIVE_CALLS: Dict[str, VapiCallSession] = {}


app = FastAPI(title="ARIA Twilio Backend", version="1.0.0")


def _get_env_or_fail(key: str) -> str:
    value = os.getenv(key, "").strip()
    if not value:
        raise HTTPException(status_code=500, detail=f"Missing required environment variable: {key}")
    return value


def _is_truthy(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _upsert_env_value(key: str, value: str) -> None:
    with ENV_UPDATE_LOCK:
        if ENV_FILE_PATH.exists():
            lines = ENV_FILE_PATH.read_text(encoding="utf-8").splitlines()
        else:
            lines = []

        replacement = f"{key}={value}"
        replaced = False
        for index, line in enumerate(lines):
            if line.startswith(f"{key}="):
                lines[index] = replacement
                replaced = True
                break

        if not replaced:
            lines.append(replacement)

        ENV_FILE_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _get_ngrok_public_url() -> str | None:
    api_url = os.getenv("NGROK_API_URL", "http://127.0.0.1:4040/api/tunnels").strip()
    if not api_url:
        return None

    try:
        with urlopen(api_url, timeout=2) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (URLError, TimeoutError, json.JSONDecodeError, OSError):
        return None

    tunnels = payload.get("tunnels", [])
    for tunnel in tunnels:
        public_url = str(tunnel.get("public_url", "")).strip()
        if public_url.startswith("https://"):
            return public_url
    return None


def _resolve_public_base_url() -> str:
    base = os.getenv("TWILIO_PUBLIC_BASE_URL", "").strip()
    auto_sync = _is_truthy(os.getenv("AUTO_SYNC_TUNNEL_URL", "false"))
    provider = os.getenv("TUNNEL_PROVIDER", "static").strip().lower()

    if auto_sync and provider == "ngrok":
        ngrok_url = _get_ngrok_public_url()
        if ngrok_url:
            if ngrok_url != base:
                os.environ["TWILIO_PUBLIC_BASE_URL"] = ngrok_url
                _upsert_env_value("TWILIO_PUBLIC_BASE_URL", ngrok_url)
                print(f"Synced TWILIO_PUBLIC_BASE_URL -> {ngrok_url}")
            return ngrok_url

    if base:
        return base

    raise HTTPException(status_code=500, detail="Missing required environment variable: TWILIO_PUBLIC_BASE_URL")


def _public_url(path: str) -> str:
    base = _resolve_public_base_url().rstrip("/")
    return f"{base}{path}"


def _get_twilio_client() -> Client:
    account_sid = _get_env_or_fail("TWILIO_ACCOUNT_SID")
    auth_token = _get_env_or_fail("TWILIO_AUTH_TOKEN")
    return Client(account_sid, auth_token)


def _safe_json_loads(raw_text: str) -> Dict[str, Any]:
    try:
        parsed = json.loads(raw_text)
        return parsed if isinstance(parsed, dict) else {}
    except json.JSONDecodeError:
        return {}


def _vapi_api_base() -> str:
    return os.getenv("VAPI_API_BASE", "https://api.vapi.ai").strip().rstrip("/")


def _vapi_webhook_url() -> str:
    configured = os.getenv("VAPI_WEBHOOK_BASE_URL", "").strip()
    base = configured if configured else _resolve_public_base_url()
    return f"{base.rstrip('/')}/vapi/webhook"


def _vapi_headers() -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {_get_env_or_fail('VAPI_API_KEY')}",
        "Content-Type": "application/json",
        "User-Agent": "ARIA-Vapi-Backend/1.0",
    }


def _vapi_error_detail(response: requests.Response) -> str:
    text = response.text.strip()
    try:
        payload = response.json()
    except ValueError:
        payload = {}

    if isinstance(payload, dict):
        for key in ("message", "error", "detail", "code"):
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()

    if text:
        return text[:500]

    return f"HTTP {response.status_code}"


def _fetch_vapi_call(call_id: str) -> Dict[str, Any]:
    try:
        response = requests.get(
            f"{_vapi_api_base()}/call/{call_id}",
            headers=_vapi_headers(),
            timeout=20,
        )
    except RequestException as exc:
        raise HTTPException(status_code=502, detail=f"Vapi sync failed: {exc}") from exc

    if response.status_code >= 400:
        raise HTTPException(status_code=400, detail=f"Vapi sync failed: {_vapi_error_detail(response)}")

    try:
        data = response.json()
    except ValueError as exc:
        raise HTTPException(status_code=502, detail="Vapi sync failed: invalid JSON response") from exc

    return data if isinstance(data, dict) else {}


def _extract_vapi_transcripts_from_call(call_data: Dict[str, Any]) -> List[str]:
    lines: List[str] = []

    def add(value: Any) -> None:
        if isinstance(value, str):
            text = value.strip()
            if text and text not in lines:
                lines.append(text)

    for container in [call_data.get("artifact"), call_data]:
        if not isinstance(container, dict):
            continue

        transcript = container.get("transcript")
        if isinstance(transcript, str):
            add(transcript)
        elif isinstance(transcript, list):
            for item in transcript:
                if isinstance(item, str):
                    add(item)
                elif isinstance(item, dict):
                    add(item.get("text"))
                    add(item.get("content"))
                    add(item.get("transcript"))

        messages = container.get("messages")
        if isinstance(messages, list):
            for message in messages:
                if not isinstance(message, dict):
                    continue
                add(message.get("text"))
                add(message.get("content"))
                add(message.get("transcript"))

    return lines


def _extract_vapi_call_id(payload: Dict[str, Any], message: Dict[str, Any]) -> str:
    candidates: List[Any] = [
        message.get("callId"),
        payload.get("callId"),
    ]

    for obj in [message.get("call"), payload.get("call"), message, payload]:
        if isinstance(obj, dict):
            candidates.append(obj.get("id"))
            candidates.append(obj.get("callId"))

    for candidate in candidates:
        if isinstance(candidate, str) and candidate.strip():
            return candidate.strip()
    return ""


def _extract_vapi_phone_number(payload: Dict[str, Any], message: Dict[str, Any]) -> str:
    containers = [
        message.get("customer"),
        payload.get("customer"),
        message.get("call"),
        payload.get("call"),
        message,
        payload,
    ]

    for container in containers:
        if not isinstance(container, dict):
            continue
        for key in ("number", "phoneNumber", "customerNumber", "to"):
            value = container.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return ""


def _extract_vapi_status(message: Dict[str, Any]) -> str:
    for key in ("status", "state", "callStatus"):
        value = message.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()

    call_info = message.get("call")
    if isinstance(call_info, dict):
        for key in ("status", "state"):
            value = call_info.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return ""


def _extract_vapi_transcript(message: Dict[str, Any]) -> str:
    def _string_candidate(value: Any) -> str:
        return value.strip() if isinstance(value, str) else ""

    direct = _string_candidate(message.get("transcript"))
    if direct:
        return direct

    for key in ("text", "content", "utterance"):
        value = _string_candidate(message.get(key))
        if value:
            return value

    transcript_obj = message.get("transcript")
    if isinstance(transcript_obj, dict):
        for key in ("text", "content", "transcript"):
            value = _string_candidate(transcript_obj.get(key))
            if value:
                return value

    artifact = message.get("artifact")
    if isinstance(artifact, dict):
        for key in ("transcript", "text", "content"):
            value = _string_candidate(artifact.get(key))
            if value:
                return value

    return ""


def _save_vapi_call_log(session: VapiCallSession) -> Dict[str, str]:
    now = datetime.now()
    filename = f"call_log_{now.strftime('%Y%m%d_%H%M%S')}.json"

    log_dir = os.getenv("CALL_LOG_DIR", "call_logs").strip() or "call_logs"
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    responses = {f"line_{index + 1}": text for index, text in enumerate(session.transcripts)}
    raw_transcript = " ".join(session.transcripts).strip()

    duration_seconds = 0
    if isinstance(session.end_report, dict):
        for key in ("durationSeconds", "duration", "callDuration", "durationInSeconds"):
            value = session.end_report.get(key)
            if isinstance(value, (int, float)):
                duration_seconds = int(value)
                break

    payload = {
        "provider": "vapi",
        "call_id": session.call_id,
        "timestamp": now.isoformat(timespec="seconds"),
        "phone_number": session.phone_number,
        "assistant_id": session.assistant_id,
        "phone_number_id": session.phone_number_id,
        "status": session.status,
        "responses": responses,
        "raw_transcript": raw_transcript,
        "call_duration_seconds": duration_seconds,
        "event_count": len(session.events),
        "events": session.events,
        "end_report": session.end_report,
    }

    full_path = log_path / filename
    full_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"\n[VAPI {session.call_id}] Saved call log -> {full_path}")
    if raw_transcript:
        print(f"[VAPI {session.call_id}] raw_transcript: {raw_transcript}\n")

    return {"filename": filename, "full_path": str(full_path)}


def _trigger_twilio_call(phone_number: str) -> Dict[str, str]:
    twilio_from = _get_env_or_fail("TWILIO_FROM_NUMBER")
    client = _get_twilio_client()

    try:
        call = client.calls.create(
            to=phone_number,
            from_=twilio_from,
            url=_public_url("/call/start"),
            method="POST",
            status_callback=_public_url("/call/complete"),
            status_callback_method="POST",
            status_callback_event=["completed"],
        )
    except TwilioRestException as exc:
        raise HTTPException(status_code=400, detail=f"Twilio call failed: {exc.msg}") from exc

    ACTIVE_CALLS[call.sid] = CallSession(call_id=call.sid, phone_number=phone_number)
    print(f"Started outbound Twilio call {call.sid} -> {phone_number}")

    return {
        "message": "Call started.",
        "provider": "twilio",
        "call_id": call.sid,
        "phone_number": phone_number,
    }


def _trigger_vapi_call(phone_number: str) -> Dict[str, str]:
    assistant_id = _get_env_or_fail("VAPI_ASSISTANT_ID")
    phone_number_id = _get_env_or_fail("VAPI_PHONE_NUMBER_ID")

    payload = {
        "assistantId": assistant_id,
        "phoneNumberId": phone_number_id,
        "customer": {
            "number": phone_number,
            "name": "Elder User",
        },
        "assistantOverrides": {
            "server": {
                "url": _vapi_webhook_url(),
            },
            "serverMessages": [
                "status-update",
                "transcript[transcriptType=\"final\"]",
                "end-of-call-report",
            ],
        },
        "name": "ARIA Daily Check-in",
    }

    try:
        response = requests.post(
            f"{_vapi_api_base()}/call",
            headers=_vapi_headers(),
            json=payload,
            timeout=30,
        )
    except RequestException as exc:
        raise HTTPException(status_code=502, detail=f"Vapi call failed: {exc}") from exc

    if response.status_code >= 400:
        raise HTTPException(status_code=400, detail=f"Vapi call failed: {_vapi_error_detail(response)}")

    try:
        data = response.json()
    except ValueError as exc:
        raise HTTPException(status_code=502, detail="Vapi call failed: invalid JSON response") from exc

    if not isinstance(data, dict):
        raise HTTPException(status_code=502, detail="Vapi call failed: malformed response")

    call_id = str(data.get("id", "")).strip()
    if not call_id:
        raise HTTPException(status_code=502, detail="Vapi call failed: missing call id in response")

    session = VapiCallSession(
        call_id=call_id,
        phone_number=phone_number,
        assistant_id=assistant_id,
        phone_number_id=phone_number_id,
        status=str(data.get("status", "queued")),
    )
    VAPI_ACTIVE_CALLS[call_id] = session

    print(f"Started outbound Vapi call {call_id} -> {phone_number}")

    return {
        "message": "Call started.",
        "provider": "vapi",
        "call_id": call_id,
        "phone_number": phone_number,
    }


def _pick_phone_number(to_number: str, from_number: str) -> str:
    if to_number and to_number.startswith("+91"):
        return to_number
    if from_number and from_number.startswith("+91"):
        return from_number
    return to_number or from_number or ""


def _session(call_sid: str, to_number: str = "", from_number: str = "") -> CallSession:
    existing = ACTIVE_CALLS.get(call_sid)
    if existing:
        if not existing.phone_number:
            existing.phone_number = _pick_phone_number(to_number, from_number)
        return existing

    new_session = CallSession(call_id=call_sid, phone_number=_pick_phone_number(to_number, from_number))
    ACTIVE_CALLS[call_sid] = new_session
    return new_session


def _say_senior_friendly(container: VoiceResponse | Gather, text: str, language: str) -> None:
    container.say(text, language=language, voice=TTS_VOICE)


def _build_language_selection_twiml(reprompt: bool = False) -> str:
    response = VoiceResponse()

    if reprompt:
        response.pause(length=LANGUAGE_REPROMPT_WAIT_SECONDS)
        _say_senior_friendly(
            response,
            "I did not receive a key press. I will repeat the language options now.",
            "en-IN",
        )

    gather = Gather(
        input="dtmf",
        num_digits=1,
        timeout=LANGUAGE_MENU_TIMEOUT_SECONDS,
        action_on_empty_result=True,
        action=_public_url("/call/language"),
        method="POST",
    )
    _say_senior_friendly(
        gather,
        "Welcome to ARIA. Please press 1 for English, 2 for Hindi, 3 for Kannada, 4 for Tamil, 5 for Telugu, 6 for Marathi.",
        "en-IN",
    )
    response.append(gather)
    return str(response)


def _question_twiml(call_sid: str, question_number: int) -> str:
    session = ACTIVE_CALLS[call_sid]
    language = LANGUAGES.get(session.language_digit, LANGUAGES["1"])
    question_text = language.questions[question_number]

    response = VoiceResponse()
    response.pause(length=SPEECH_PRE_PROMPT_PAUSE_SECONDS)
    gather = Gather(
        input="speech",
        timeout=QUESTION_GATHER_TIMEOUT_SECONDS,
        speech_timeout="auto",
        action_on_empty_result=True,
        language=language.code,
        action=f"{_public_url('/call/answer')}?question={question_number}",
        method="POST",
    )
    _say_senior_friendly(gather, question_text, language.code)
    response.append(gather)
    return str(response)


def _save_call_log(session: CallSession, call_duration_seconds: int) -> Dict[str, str]:
    now = datetime.now()
    filename = f"call_log_{now.strftime('%Y%m%d_%H%M%S')}.json"

    log_dir = os.getenv("CALL_LOG_DIR", "call_logs").strip() or "call_logs"
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    ordered_answers = [session.responses.get(f"question_{index}", "") for index in range(1, 5)]
    raw_transcript = " ".join(answer for answer in ordered_answers if answer).strip()

    payload = {
        "call_id": session.call_id,
        "timestamp": now.isoformat(timespec="seconds"),
        "phone_number": session.phone_number,
        "language_chosen": session.language_chosen,
        "language_code": session.language_code,
        "responses": session.responses,
        "raw_transcript": raw_transcript,
        "call_duration_seconds": call_duration_seconds,
    }

    full_path = log_path / filename
    full_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"\n[{session.call_id}] Saved call log -> {full_path}")
    for question_key in sorted(session.responses.keys()):
        print(f"[{session.call_id}] {question_key}: {session.responses[question_key]}")
    print(f"[{session.call_id}] raw_transcript: {raw_transcript}\n")

    return {"filename": filename, "full_path": str(full_path)}


def _extract_phone_number(raw_value: str) -> str:
    value = (raw_value or "").strip()
    if not PHONE_PATTERN.fullmatch(value):
        raise HTTPException(
            status_code=400,
            detail="Phone number must be in +91XXXXXXXXXX format (India only).",
        )
    return value


@app.get("/")
async def health() -> Dict[str, str]:
    provider = os.getenv("CALL_PROVIDER", "twilio").strip().lower() or "twilio"
    return {
        "status": "ok",
        "message": "ARIA Twilio backend is running.",
        "provider": provider,
        "trigger_call": "POST /call/trigger",
    }


@app.post("/call/trigger")
async def call_trigger(request: Request) -> Dict[str, str]:
    content_type = request.headers.get("content-type", "")
    phone_number = ""

    if "application/json" in content_type:
        body = await request.json()
        phone_number = str(body.get("phone_number", "")).strip()
    else:
        form = await request.form()
        phone_number = str(form.get("phone_number", "")).strip()

    phone_number = _extract_phone_number(phone_number)

    provider = os.getenv("CALL_PROVIDER", "twilio").strip().lower() or "twilio"
    if provider == "vapi":
        return _trigger_vapi_call(phone_number)
    return _trigger_twilio_call(phone_number)


@app.post("/vapi/call/trigger")
async def vapi_call_trigger(request: Request) -> Dict[str, str]:
    content_type = request.headers.get("content-type", "")
    phone_number = ""

    if "application/json" in content_type:
        body = await request.json()
        phone_number = str(body.get("phone_number", "")).strip()
    else:
        form = await request.form()
        phone_number = str(form.get("phone_number", "")).strip()

    phone_number = _extract_phone_number(phone_number)
    return _trigger_vapi_call(phone_number)


@app.post("/vapi/webhook")
async def vapi_webhook(request: Request) -> JSONResponse:
    payload_raw = await request.body()
    payload = _safe_json_loads(payload_raw.decode("utf-8", errors="ignore"))
    message = payload.get("message") if isinstance(payload.get("message"), dict) else {}
    message_type = str(message.get("type", "unknown")).strip() or "unknown"

    call_id = _extract_vapi_call_id(payload, message)
    if not call_id:
        return JSONResponse({"status": "ignored", "reason": "missing call id"})

    phone_number = _extract_vapi_phone_number(payload, message)
    session = VAPI_ACTIVE_CALLS.get(call_id)
    if session is None:
        session = VapiCallSession(call_id=call_id, phone_number=phone_number)

    if phone_number and not session.phone_number:
        session.phone_number = phone_number

    status = _extract_vapi_status(message)
    if status:
        session.status = status

    transcript = _extract_vapi_transcript(message)
    if transcript and transcript not in session.transcripts:
        session.transcripts.append(transcript)
        print(f"[VAPI {call_id}] transcript: {transcript}")

    event: Dict[str, Any] = {
        "type": message_type,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }
    if status:
        event["status"] = status
    if transcript:
        event["text"] = transcript
    session.events.append(event)

    if message_type == "end-of-call-report":
        session.end_report = message

    VAPI_ACTIVE_CALLS[call_id] = session

    should_finalize = message_type == "end-of-call-report"

    if should_finalize:
        save_info = _save_vapi_call_log(session)
        VAPI_ACTIVE_CALLS.pop(call_id, None)
        return JSONResponse(
            {
                "status": "saved",
                "provider": "vapi",
                "call_id": call_id,
                "log_file": save_info["filename"],
                "full_path": save_info["full_path"],
            }
        )

    return JSONResponse({"status": "ok", "provider": "vapi", "call_id": call_id, "event_type": message_type})


@app.post("/vapi/call/sync/{call_id}")
async def vapi_call_sync(call_id: str) -> JSONResponse:
    call_data = _fetch_vapi_call(call_id)

    call_info = call_data if isinstance(call_data, dict) else {}
    customer = call_info.get("customer") if isinstance(call_info.get("customer"), dict) else {}
    phone_number = str(customer.get("number", "")).strip()

    session = VAPI_ACTIVE_CALLS.get(call_id)
    if session is None:
        session = VapiCallSession(call_id=call_id, phone_number=phone_number)

    if phone_number and not session.phone_number:
        session.phone_number = phone_number

    status = str(call_info.get("status", "")).strip()
    if status:
        session.status = status

    for line in _extract_vapi_transcripts_from_call(call_info):
        if line not in session.transcripts:
            session.transcripts.append(line)

    sync_event: Dict[str, Any] = {
        "type": "sync-fetch",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "status": session.status,
    }
    ended_reason = call_info.get("endedReason")
    if isinstance(ended_reason, str) and ended_reason.strip():
        sync_event["endedReason"] = ended_reason.strip()
    session.events.append(sync_event)

    session.end_report = {
        "source": "vapi-call-sync",
        "status": session.status,
        "endedReason": ended_reason,
    }

    VAPI_ACTIVE_CALLS[call_id] = session

    if session.status.lower() in {"ended", "completed"}:
        save_info = _save_vapi_call_log(session)
        VAPI_ACTIVE_CALLS.pop(call_id, None)
        return JSONResponse(
            {
                "status": "saved",
                "provider": "vapi",
                "call_id": call_id,
                "log_file": save_info["filename"],
                "full_path": save_info["full_path"],
            }
        )

    return JSONResponse({
        "status": "synced",
        "provider": "vapi",
        "call_id": call_id,
        "call_status": session.status,
        "transcript_lines": len(session.transcripts),
    })


@app.post("/call/start", response_class=PlainTextResponse)
async def call_start(
    CallSid: str = Form(""),
    From: str = Form(""),
    To: str = Form(""),
) -> str:
    if CallSid:
        _session(CallSid, To, From)
    return _build_language_selection_twiml()


@app.post("/call/language", response_class=PlainTextResponse)
async def call_language(
    CallSid: str = Form(""),
    Digits: str = Form(""),
    From: str = Form(""),
    To: str = Form(""),
) -> str:
    if not CallSid:
        raise HTTPException(status_code=400, detail="Missing CallSid")

    session = _session(CallSid, To, From)

    selected = Digits.strip() if Digits else ""
    if not selected:
        return _build_language_selection_twiml(reprompt=True)

    if selected not in LANGUAGES:
        return _build_language_selection_twiml(reprompt=True)

    pack = LANGUAGES[selected]
    session.language_digit = selected
    session.language_chosen = pack.name
    session.language_code = pack.code

    response = VoiceResponse()
    response.pause(length=SPEECH_PRE_PROMPT_PAUSE_SECONDS)
    _say_senior_friendly(response, pack.confirmation, pack.code)

    first_question = Gather(
        input="speech",
        timeout=QUESTION_GATHER_TIMEOUT_SECONDS,
        speech_timeout="auto",
        action_on_empty_result=True,
        language=pack.code,
        action=f"{_public_url('/call/answer')}?question=1",
        method="POST",
    )
    _say_senior_friendly(first_question, pack.questions[1], pack.code)
    response.append(first_question)

    return str(response)


@app.post("/call/answer", response_class=PlainTextResponse)
async def call_answer(
    question: int,
    CallSid: str = Form(""),
    SpeechResult: str = Form(""),
    From: str = Form(""),
    To: str = Form(""),
) -> str:
    if not CallSid:
        raise HTTPException(status_code=400, detail="Missing CallSid")
    if question < 1 or question > 4:
        raise HTTPException(status_code=400, detail="question must be between 1 and 4")

    session = _session(CallSid, To, From)

    transcript = (SpeechResult or "").strip() or "[no speech captured]"
    key = f"question_{question}"
    session.responses[key] = transcript

    print(f"[{CallSid}] {key}: {transcript}")

    if question < 4:
        return _question_twiml(CallSid, question + 1)

    pack = LANGUAGES.get(session.language_digit, LANGUAGES["1"])
    response = VoiceResponse()
    response.pause(length=SPEECH_PRE_PROMPT_PAUSE_SECONDS)
    _say_senior_friendly(response, pack.close, pack.code)
    response.hangup()
    return str(response)


@app.post("/call/complete")
async def call_complete(
    CallSid: str = Form(""),
    CallDuration: str = Form("0"),
    From: str = Form(""),
    To: str = Form(""),
) -> JSONResponse:
    if not CallSid:
        raise HTTPException(status_code=400, detail="Missing CallSid")

    session = ACTIVE_CALLS.get(CallSid)
    if session is None:
        session = CallSession(call_id=CallSid, phone_number=_pick_phone_number(To, From))

    try:
        duration_seconds = int(CallDuration)
    except (TypeError, ValueError):
        duration_seconds = 0

    save_info = _save_call_log(session, duration_seconds)
    ACTIVE_CALLS.pop(CallSid, None)

    return JSONResponse(
        {
            "status": "saved",
            "call_id": CallSid,
            "log_file": save_info["filename"],
            "full_path": save_info["full_path"],
        }
    )


@app.get("/call/live/{call_id}")
async def call_live(call_id: str) -> Dict[str, object]:
    session = ACTIVE_CALLS.get(call_id)
    if not session:
        raise HTTPException(status_code=404, detail="Call not found in active memory")

    return {
        "call_id": session.call_id,
        "phone_number": session.phone_number,
        "language_chosen": session.language_chosen,
        "language_code": session.language_code,
        "responses": session.responses,
    }


@app.get("/vapi/call/live/{call_id}")
async def vapi_call_live(call_id: str) -> Dict[str, Any]:
    session = VAPI_ACTIVE_CALLS.get(call_id)
    if not session:
        raise HTTPException(status_code=404, detail="Vapi call not found in active memory")

    return {
        "provider": "vapi",
        "call_id": session.call_id,
        "phone_number": session.phone_number,
        "status": session.status,
        "transcripts": session.transcripts,
        "event_count": len(session.events),
    }
