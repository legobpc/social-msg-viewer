import os
import asyncio
from telethon import TelegramClient
from dotenv import load_dotenv
from fastapi import Depends
from app.auth_routes import get_current_user

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

def get_user_client(user):
    session_name = f"user_{user.id}"
    return TelegramClient(session_name, API_ID, API_HASH)

def get_lock(user_id, session_locks):
    if user_id not in session_locks:
        session_locks[user_id] = asyncio.Lock()
    return session_locks[user_id]