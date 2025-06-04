# main.py

import os
import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from telethon import TelegramClient, errors
from telethon.tl.functions.contacts import ImportContactsRequest
from telethon.tl.types import InputPhoneContact
from dotenv import load_dotenv

# ───────────────────────────────────────────────────────────────────────────────
# 1️⃣ Umgebungsvariablen laden
# ───────────────────────────────────────────────────────────────────────────────
load_dotenv()  # lädt .env, falls du lokal testest

raw_api_id = os.getenv("TELEGRAM_API_ID")
api_hash   = os.getenv("TELEGRAM_API_HASH")
phone      = os.getenv("TELEGRAM_PHONE")

# Prüfen, dass alle drei Variablen vorhanden sind
if raw_api_id is None or api_hash is None or phone is None:
    raise RuntimeError(
        "Eine oder mehrere Env-Variablen fehlen: TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_PHONE"
    )

try:
    api_id = int(raw_api_id)
except ValueError:
    raise RuntimeError("TELEGRAM_API_ID muss eine ganze Zahl sein.")

# ───────────────────────────────────────────────────────────────────────────────
# 2️⃣ TelegramClient & FastAPI-Instanz
# ───────────────────────────────────────────────────────────────────────────────
# Verwende die bereits autorisierte railway_verifier_session.session
client = TelegramClient("railway_verifier_session", api_id, api_hash)

app = FastAPI()

# ───────────────────────────────────────────────────────────────────────────────
# 3️⃣ Keep-Alive-Task (Hält Telethon-Session aktiv)
# ───────────────────────────────────────────────────────────────────────────────
async def keep_alive():
    """
    Endlosschleife, die alle 30 Minuten (1800 Sekunden) hineincheckt:
    - ruft client.get_me() auf, um den Auth-Key aktiv zu halten.
    - tritt in eine asyncio.sleep(1800), bevor sie es erneut probiert.
    """
    await client.connect()  # sicherstellen, dass eine Verbindung da ist
    while True:
        try:
            # Einfaches RPC, um Session-Verfall zu verhindern
            await client.get_me()
        except Exception as e:
            # Falls Telethon hier einmal scheitert, loggen wir den Fehler,
            # brechen aber nicht ab. Beim nächsten Zyklus versuchen wir es wieder.
            print(f"[KeepAlive] Telethon-Error: {e}")
        # Warte 30 Minuten (1800 Sekunden) bis zum nächsten Keep-Alive
        await asyncio.sleep(1800)

# ───────────────────────────────────────────────────────────────────────────────
# 4️⃣ Startup- und Shutdown-Handler für FastAPI
# ───────────────────────────────────────────────────────────────────────────────
@app.on_event("startup")
async def startup():
    # 1) Telethon-Client verbinden
    await client.connect()

    # 2) Prüfen, ob Session autorisiert ist
    if not await client.is_user_authorized():
        # Falls hier False, dann hat die Session wohl nicht geladen oder ist ungültig
        raise RuntimeError(
            "Telegram-Session nicht autorisiert. "
            "Führe lokal 'python main.py' aus, um die Session zu autorisieren."
        )

    # 3) Starte Keep-Alive-Task im Hintergrund (daemon)
    #    Dadurch bleibt die Session auch über Inaktivität hinweg gültig.
    asyncio.create_task(keep_alive())


@app.on_event("shutdown")
async def shutdown():
    await client.disconnect()


# ───────────────────────────────────────────────────────────────────────────────
# 5️⃣ Pydantic-Schema
# ───────────────────────────────────────────────────────────────────────────────
class Number(BaseModel):
    phone_number: str


# ───────────────────────────────────────────────────────────────────────────────
# 6️⃣ Endpoint: POST /verify
# ───────────────────────────────────────────────────────────────────────────────
@app.post("/verify")
async def verify_number(payload: Number):
    """
    Importiert einen Kontakt in Telegram:
    - Wenn der User existiert, ist result.users[0] nicht None → telegram_user = True
    - Andernfalls telegram_user = False
    """
    contact = InputPhoneContact(
        client_id=0,
        phone=payload.phone_number,
        first_name="Check",
        last_name="User"
    )

    try:
        result = await client(ImportContactsRequest([contact]))
    except errors.FloodWaitError as e:
        # Telegram hat dich „geflutet“. Warte X Sekunden.
        raise HTTPException(status_code=429, detail=f"Telegram-FloodWait: bitte {e.seconds}s warten")
    except errors.RPCError as e:
        # Einzelne RPC-Fehler (z. B. Nummer falsch formatiert) abfangen
        raise HTTPException(status_code=500, detail=f"Telegram-RPC-Fehler: {e}")

    user = result.users[0] if result.users else None
    return {
        "phone_number": payload.phone_number,
        "telegram_user": user is not None
    }


# ───────────────────────────────────────────────────────────────────────────────
# 7️⃣ Lokaler Start-Block (nur für 'python main.py')
# ───────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)