import asyncio
from telethon import TelegramClient

from config import API_ID, API_HASH, SESSION, MEDIA_DIR, BOT_TOKEN, ADMIN_ID, BOT_ID
from db import init_db
from handlers import register_handlers
from notifier import Notifier

async def main():
    if not BOT_TOKEN:
        raise RuntimeError("TG_BOT_TOKEN is required for notifications")
    if not ADMIN_ID:
        raise RuntimeError("TG_ADMIN_ID is required for notifications")

    conn = init_db("messages.db")

    user_client = TelegramClient(SESSION, API_ID, API_HASH)
    bot_client = TelegramClient("notifier_bot", API_ID, API_HASH)

    await bot_client.start(bot_token=BOT_TOKEN)
    notifier = Notifier(bot_client, ADMIN_ID)

    await user_client.start()
    session_user = await user_client.get_me()
    register_handlers(user_client, notifier, conn, MEDIA_DIR, session_user, BOT_ID)

    await notifier.notify("Userbot is online")
    print("Userbot started")

    async with user_client:
        await user_client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())