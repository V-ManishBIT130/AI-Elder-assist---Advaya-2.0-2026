# AI-Elder-assist---Advaya-2.0-2026

## Twilio Voice Call Backend (FastAPI)

This project includes a Twilio voice backend that:
- asks language using keypad input
- asks 4 voice questions in that language
- captures Twilio speech transcription for each answer
- saves a call JSON log on call completion

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Create `.env`

Copy `.env.example` to `.env` and fill values:

```env
TWILIO_ACCOUNT_SID=ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_FROM_NUMBER=+1XXXXXXXXXX
TWILIO_PUBLIC_BASE_URL=https://your-ngrok-subdomain.ngrok-free.app
CALL_LOG_DIR=call_logs
```

### 3. Run backend

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Expose backend to Twilio

Use ngrok:

```bash
ngrok http 8000
```

Set `TWILIO_PUBLIC_BASE_URL` to the https ngrok URL.

### 5. Start a call to India number (+91 only)

Use CLI prompt:

```bash
python backend/start_call_cli.py
```

Enter number in this exact format:

```text
+91XXXXXXXXXX
```

Or trigger by API:

```bash
curl -X POST http://127.0.0.1:8000/call/trigger \
	-H "Content-Type: application/json" \
	-d '{"phone_number":"+91XXXXXXXXXX"}'
```

### Webhook Endpoints

- `POST /call/start` -> language selection TwiML
- `POST /call/language` -> language chosen, asks first question
- `POST /call/answer` -> stores transcription and asks next question
- `POST /call/complete` -> saves final JSON log to file

### Live transcript view during call

```text
GET /call/live/{call_id}
```

The backend also prints each question transcription in terminal as it is captured.
