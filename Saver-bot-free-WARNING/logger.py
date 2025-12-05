from telethon import TelegramClient
from config import LOG_ENABLED

async def log(client: TelegramClient, text: str):
    if not LOG_ENABLED:
        return
    try:
        await client.send_message("me", text)
    except Exception as e:
        print(f"[log failed] {e}")