import os

async def download_media_safe(message, media_dir: str):
    os.makedirs(media_dir, exist_ok=True)
    if not message.media:
        return None
    try:
        return await message.download_media(file=media_dir)
    except Exception as e:
        print(f"[media download failed] chat={message.chat_id} msg={message.id} err={e}")
        return None