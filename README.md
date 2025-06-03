# Telegram Number Verifier API

This FastAPI service verifies if a phone number is registered on Telegram.

## Usage
POST to `/verify` with:
```json
{
  "phone_number": "+491761234567"
}
```
Returns:
```json
{
  "phone_number": "+491761234567",
  "telegram_user": true
}
```

## Setup Locally (First Login)
1. Create a `.env` file or export:
```
export TELEGRAM_API_ID=...
export TELEGRAM_API_HASH=...
export TELEGRAM_PHONE=+49...
```
2. Run:
```
python main.py
```
This will prompt you to log in via code and store the session file.
