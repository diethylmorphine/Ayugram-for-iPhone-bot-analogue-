import os
from typing import Optional


class Notifier:
    def __init__(self, bot_client, admin_id: int):
        self.bot = bot_client
        self.admin_id = admin_id

    async def notify(self, text: str):
        if not self.admin_id:
            return
        try:
            await self.bot.send_message(self.admin_id, text)
        except Exception as e:
            print(f"[notify failed] {e}")

    async def send_view_once(self, media_path: str, caption: Optional[str] = None):
        if not self.admin_id or not media_path:
            return
        if not os.path.exists(media_path):
            await self.notify(f"[view-once] missing file: {media_path}")
            return
        try:
            await self.bot.send_file(self.admin_id, media_path, caption=caption or None)
        except Exception as e:
            print(f"[view-once send failed] {e}")