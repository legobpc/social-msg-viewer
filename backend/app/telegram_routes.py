import os
from fastapi import APIRouter, Query, Depends, HTTPException
from telethon.errors import SessionPasswordNeededError, AuthKeyUnregisteredError
from app.auth_routes import get_current_user
from app.telegram import utils as tg_utils

PHONE = os.getenv("PHONE")
TG_PASSWORD = os.getenv("TG_PASSWORD")

router = APIRouter()
session_data = {}
session_lock = {}

@router.get("/connect", response_model=None)
async def connect(user=Depends(get_current_user)):
    lock = tg_utils.get_lock(user.id, session_lock)
    async with lock:
        client = tg_utils.get_user_client(user)
        await client.connect()
        try:
            if not await client.is_user_authorized():
                result = await client.send_code_request(PHONE)
                session_data[user.id] = result.phone_code_hash
                return {"message": "Code sent to Telegram. Use /login?code=XXXX"}
            return {"message": "Already authorized"}
        finally:
            await client.disconnect()

@router.get("/login", response_model=None)
async def login(code: str, user=Depends(get_current_user)):
    lock = tg_utils.get_lock(user.id, session_lock)
    async with lock:
        client = tg_utils.get_user_client(user)
        await client.connect()
        try:
            if not await client.is_user_authorized():
                phone_code_hash = session_data.get(user.id)
                if not phone_code_hash:
                    raise HTTPException(status_code=400, detail="Missing phone_code_hash")

                try:
                    await client.sign_in(PHONE, code, phone_code_hash=phone_code_hash)
                except SessionPasswordNeededError:
                    await client.sign_in(password=TG_PASSWORD)

                return {"message": "Logged in"}
            return {"message": "Already authorized"}
        finally:
            await client.disconnect()

@router.get("/me", response_model=None)
async def get_me(user=Depends(get_current_user)):
    lock = tg_utils.get_lock(user.id, session_lock)
    async with lock:
        client = tg_utils.get_user_client(user)
        await client.connect()
        try:
            if not await client.is_user_authorized():
                raise HTTPException(status_code=401, detail="Telegram not authorized")
            me = await client.get_me()
            if not me:
                raise HTTPException(status_code=500, detail="Could not fetch Telegram profile")
            return {
                "user_id": me.id,
                "username": me.username,
                "first_name": me.first_name,
                "phone": me.phone
            }
        finally:
            await client.disconnect()

@router.get("/chats", response_model=None)
async def get_chats(user=Depends(get_current_user)):
    lock = tg_utils.get_lock(user.id, session_lock)
    async with lock:
        client = tg_utils.get_user_client(user)
        await client.connect()
        try:
            if not await client.is_user_authorized():
                raise HTTPException(status_code=401, detail="Telegram not authorized")

            dialogs = await client.get_dialogs()
            result = []
            for dialog in dialogs:
                entity = dialog.entity
                result.append({
                    "id": entity.id,
                    "title": getattr(entity, "title", None),
                    "username": getattr(entity, "username", None),
                    "type": type(entity).__name__
                })
            return result
        finally:
            await client.disconnect()

@router.get("/messages", response_model=None)
async def get_messages(
    chat_id: int = Query(None),
    username: str = Query(None),
    user=Depends(get_current_user)
):
    lock = tg_utils.get_lock(user.id, session_lock)
    async with lock:
        client = tg_utils.get_user_client(user)
        await client.connect()
        try:
            if username:
                try:
                    entity = await client.get_entity(username)
                except Exception as e:
                    return {"error": f"Could not find username '{username}': {str(e)}"}
            elif chat_id:
                dialogs = await client.get_dialogs()
                entity = next((d.entity for d in dialogs if getattr(d.entity, "id", None) == chat_id), None)
                if not entity:
                    return {"error": f"Chat ID {chat_id} not found in dialogs"}
            else:
                return {"error": "You must provide chat_id or username"}

            messages = []
            async for msg in client.iter_messages(entity, limit=20):
                messages.append({
                    "id": msg.id,
                    "text": msg.text,
                    "date": str(msg.date),
                    "from_id": getattr(msg.from_id, 'user_id', None),
                })

            return messages
        finally:
            await client.disconnect()

@router.post("/logout", response_model=None)
async def logout(user=Depends(get_current_user)):
    lock = tg_utils.get_lock(user.id, session_lock)
    async with lock:
        client = tg_utils.get_user_client(user)
        await client.connect()
        try:
            await client.log_out()
        finally:
            await client.disconnect()

        session_file = f"user_{user.id}.session"
        try:
            os.remove(session_file)
        except FileNotFoundError:
            pass

        return {"message": "Logged out from Telegram"}
