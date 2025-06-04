from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from telethon import TelegramClient, errors
from telethon.tl.functions.contacts import ImportContactsRequest
from telethon.tl.types import InputPhoneContact
from dotenv import load_dotenv
import os

# ───────────────────────────────────────────────────────────────────────────────
# 1️⃣ Load environment (muss vor dem Zugriff auf os.getenv stehen)
# ───────────────────────────────────────────────────────────────────────────────
load_dotenv()  # Liest .env im Arbeitsverzeichnis


raw_api_id = os.getenv("TELEGRAM_API_ID")
api_hash   = os.getenv("TELEGRAM_API_HASH")
phone      = os.getenv("TELEGRAM_PHONE")


if raw_api_id is None or api_hash is None or phone is None:
    raise RuntimeError(
        "Eine oder mehrere Umgebungsvariablen fehlen: "
        "TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_PHONE"
    )

try:
    api_id = int(raw_api_id)
except ValueError:
    raise RuntimeError("TELEGRAM_API_ID muss eine ganze Zahl sein.")

session_name = "railway_verifier_session"

# ───────────────────────────────────────────────────────────────────────────────
# 2️⃣ FastAPI & Telethon-Setup
# ───────────────────────────────────────────────────────────────────────────────
app = FastAPI()
client = TelegramClient(session_name, api_id, api_hash)

@app.on_event("startup")
async def startup():

    await client.connect()
    if not await client.is_user_authorized():
       
        raise RuntimeError(
            "Telegram-Session nicht autorisiert. "
            "Führe 'python main.py' lokal durch, um die Session zu authentifizieren."
        )

@app.on_event("shutdown")
async def shutdown():
 
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

    contact = InputPhoneContact(
        client_id=0,
        phone=payload.phone_number,
        first_name="Check",
        last_name="User"
    )
    try:
        result = await client(ImportContactsRequest([contact]))
    except errors.RPCError as e:
        # z. B. FloodWaitError oder andere Telegram-Fehler
        raise HTTPException(status_code=500, detail=f"Telegram-Fehler: {e}")

    user = result.users[0] if result.users else None
    return {
        "phone_number": payload.phone_number,
        "telegram_user": user is not None
    }

# ───────────────────────────────────────────────────────────────────────────────
# 5️⃣ Lokaler Start-Block (nur für `python main.py`)
# ───────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)