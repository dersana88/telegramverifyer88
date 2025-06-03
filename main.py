from fastapi import FastAPI
from pydantic import BaseModel
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

client = TelegramClient(session_name, api_id, api_hash)

@app.on_event("startup")
async def startup():
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
    result = await client(ImportContactsRequest([contact]))
    user = result.users[0] if result.users else None
    return {
        "phone_number": payload.phone_number,
        "telegram_user": user is not None
    }
