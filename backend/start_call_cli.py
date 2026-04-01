from __future__ import annotations

import os
import re

from dotenv import load_dotenv
from twilio.rest import Client


PHONE_PATTERN = re.compile(r"^\+91\d{10}$")


def require_env(key: str) -> str:
    value = os.getenv(key, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {key}")
    return value


def main() -> None:
    load_dotenv()

    number = input("Enter phone number to call (+91XXXXXXXXXX): ").strip()
    if not PHONE_PATTERN.fullmatch(number):
        raise SystemExit("Invalid number. Use +91 followed by 10 digits.")

    account_sid = require_env("TWILIO_ACCOUNT_SID")
    auth_token = require_env("TWILIO_AUTH_TOKEN")
    from_number = require_env("TWILIO_FROM_NUMBER")
    public_base_url = require_env("TWILIO_PUBLIC_BASE_URL").rstrip("/")

    client = Client(account_sid, auth_token)
    call = client.calls.create(
        to=number,
        from_=from_number,
        url=f"{public_base_url}/call/start",
        method="POST",
        status_callback=f"{public_base_url}/call/complete",
        status_callback_method="POST",
        status_callback_event=["completed"],
    )

    print(f"Call started. CallSid: {call.sid}")


if __name__ == "__main__":
    main()
