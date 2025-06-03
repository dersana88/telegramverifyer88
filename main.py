from fastapi import FastAPI
from pydantic import BaseModel
<<<<<<< HEAD
from telethon.sync import TelegramClient
from telethon.tl.functions.contacts import ImportContactsRequest
from telethon.tl.types import InputPhoneContact
from telethon.errors import SessionPasswordNeededError
import os

app = FastAPI()

api_id = int(os.environ.get("TELEGRAM_API_ID"))
api_hash = os.environ.get("TELEGRAM_API_HASH")
phone = os.environ.get("TELEGRAM_PHONE")
session_name = "railway_verifier_session"

=======
from telethon import TelegramClient
from telethon.tl.functions.contacts import ImportContactsRequest
from telethon.tl.types import InputPhoneContact
from dotenv import load_dotenv
import os

# ───────────────────────────────────────────────────────────────────────────────
# 1️⃣ Load environment
# ───────────────────────────────────────────────────────────────────────────────
load_dotenv()  # Liest .env und setzt os.environ

api_id = int(os.getenv("TELEGRAM_API_ID"))       # Numeric, zwingend
api_hash = os.getenv("TELEGRAM_API_HASH")        # String, zwingend
phone = os.getenv("TELEGRAM_PHONE")              # Deine Nummer, zwingend
session_name = "railway_verifier_session"        # Lokale Session-Datei

# ───────────────────────────────────────────────────────────────────────────────
# 2️⃣ FastAPI & Telethon-Setup
# ───────────────────────────────────────────────────────────────────────────────
app = FastAPI()

# Async-Telethon-Client initialisieren (noch nicht verbunden)
>>>>>>> ab3e4cc (Lokaler Build erfolgreich: FastAPI & Telethon laufen)
client = TelegramClient(session_name, api_id, api_hash)

@app.on_event("startup")
async def startup():
<<<<<<< HEAD
    await client.connect()
    if not await client.is_user_authorized():
        await client.send_code_request(phone)
        raise Exception("Login required. Run locally to complete session auth.")

@app.on_event("shutdown")
async def shutdown():
    await client.disconnect()

class Number(BaseModel):
    phone_number: str

@app.post("/verify")
async def verify_number(payload: Number):
    contact = InputPhoneContact(client_id=0, phone=payload.phone_number, first_name="Check", last_name="User")
=======
    """
    Startup-Event:  
    - Baut Verbindung zu Telegram auf.  
    - Interaktives Login (Code + 2FA) beim ersten Run.
    """
    await client.start(phone=phone)
    # Nach dem Login liegt „railway_verifier_session.session“ im Projekt-Root.

@app.on_event("shutdown")
async def shutdown():
    """
    Shutdown-Event:  
    - Trennt Verbindung sauber, um Ressourcen zu schonen.
    """
    await client.disconnect()

# ───────────────────────────────────────────────────────────────────────────────
# 3️⃣ Pydantic-Schema
# ───────────────────────────────────────────────────────────────────────────────
class Number(BaseModel):
    phone_number: str

# ───────────────────────────────────────────────────────────────────────────────
# 4️⃣ Endpoint: /verify
# ───────────────────────────────────────────────────────────────────────────────
@app.post("/verify")
async def verify_number(payload: Number):
    """
    RPC-Call zu Telegram:  
    - Importiert den Kontakt.  
    - Wenn Telegram-User existiert → True, sonst False.
    """
    contact = InputPhoneContact(
        client_id=0,
        phone=payload.phone_number,
        first_name="Check",
        last_name="User"
    )
>>>>>>> ab3e4cc (Lokaler Build erfolgreich: FastAPI & Telethon laufen)
    result = await client(ImportContactsRequest([contact]))
    user = result.users[0] if result.users else None
    return {
        "phone_number": payload.phone_number,
        "telegram_user": user is not None
    }
<<<<<<< HEAD
=======

# ───────────────────────────────────────────────────────────────────────────────
# 5️⃣ Lokaler Start-Block (nur für `python main.py`)
# ───────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
>>>>>>> ab3e4cc (Lokaler Build erfolgreich: FastAPI & Telethon laufen)
