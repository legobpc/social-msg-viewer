import os
from fastapi import APIRouter, Query, Depends
from app.telegram import client
from telethon.errors import SessionPasswordNeededError
from app.auth_routes import get_current_user

router = APIRouter()

# Connect to Telegram account (sends login code if not authorized)
@router.get("/connect")
async def connect(user=Depends(get_current_user)):
    await client.connect()
    if not await client.is_user_authorized():
        phone = os.getenv("PHONE")
        await client.send_code_request(phone)
        return {"message": "Code sent to Telegram. Use /login?code=XXXX"}
    return {"message": "Already authorized"}


# Log in to Telegram using received code (handles 2FA if needed)
@router.get("/login")
async def login(code: str, user=Depends(get_current_user)):
    await client.connect()
    if not await client.is_user_authorized():
        phone = os.getenv("PHONE")
        try:
            await client.sign_in(phone, code)
        except SessionPasswordNeededError:
            password = os.getenv("TG_PASSWORD")
            await client.sign_in(password=password)
        return {"message": "Logged in"}
    return {"message": "Already authorized"}


# Get information about the currently logged-in Telegram user
@router.get("/me")
async def get_me(user=Depends(get_current_user)):
    await client.connect()
    me = await client.get_me()
    return {
        "user_id": me.id,
        "username": me.username,
        "first_name": me.first_name,
        "phone": me.phone
    }


# Get a list of all available Telegram chats
@router.get("/chats")
async def get_chats(user=Depends(get_current_user)):
    await client.connect()
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


# Get messages from a specific Telegram chat by chat_id or username
@router.get("/messages")
async def get_messages(
    chat_id: int = Query(None),
    username: str = Query(None),
    user=Depends(get_current_user)
):
    await client.connect()

    if username:
        try:
            entity = await client.get_entity(username)
        except Exception as e:
            return {"error": f"Could not find username '{username}': {str(e)}"}
    elif chat_id:
        dialogs = await client.get_dialogs()
        entity = next((d.entity for d in dialogs if d.id == chat_id), None)
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


# Log out from the connected Telegram account and clear session
@router.post("/logout")
async def logout(user=Depends(get_current_user)):
    await client.connect()

    if not await client.is_user_authorized():
        return {"message": "Not logged in"}

    await client.log_out()
    await client.disconnect()

    try:
        os.remove("anon.session")
    except FileNotFoundError:
        pass

    return {"message": "Logged out from Telegram"}