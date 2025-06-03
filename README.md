<<<<<<< HEAD
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
=======
# Telegram Verifier

Dieses Repository enthält den kompletten FastAPI-Service, 
um über Telethon zu prüfen, ob eine Telefonnummer bei Telegram registriert ist.

## Setup

1. Virtuelle Umgebung erstellen:  
   python -m venv .venv  
   source .venv/bin/activate

2. Dependencies installieren:  
   pip install -r requirements.txt

3. `.env` mit deinen Telegram-Keys befüllen:
   TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_PHONE

4. Lokal starten:  
   python main.py  

   → Swagger: http://127.0.0.1:8000/docs

5. Produktion:  
   - Procfile ist konfiguriert für `uvicorn main:app --host 0.0.0.0 --port \$PORT`  
   - Deploy z. B. via Railway.  
>>>>>>> ab3e4cc (Lokaler Build erfolgreich: FastAPI & Telethon laufen)
