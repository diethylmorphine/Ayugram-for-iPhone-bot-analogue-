import asyncio
from datetime import datetime
from telethon import events
from telethon.errors import FloodWaitError

from media import download_media_safe


def register_handlers(user_client, notifier, conn, media_dir: str, session_user=None, bot_id: int | None = None):
    cur = conn.cursor()

    def format_user(user):
        if not user:
            return "<unknown>"
        username = getattr(user, "username", None)
        if username:
            return f"@{username}"
        full_name = " ".join(filter(None, [getattr(user, "first_name", None), getattr(user, "last_name", None)])).strip()
        return full_name or f"id {getattr(user, 'id', 'n/a')}"

    session_user_tag = format_user(session_user)

    def format_text_block(value, empty_placeholder="<empty>", missing_placeholder="<data unavailable>"):
        if value is None:
            return missing_placeholder
        return value if value else empty_placeholder

    async def resolve_user_tag(event_sender=None, sender_id=None, stored_display=None):
        if event_sender is not None:
            return format_user(event_sender)
        if stored_display:
            return stored_display
        if sender_id:
            try:
                entity = await user_client.get_entity(sender_id)
                return format_user(entity)
            except Exception:
                return f"id {sender_id}"
        return "<unknown>"

    def is_view_once(msg):
        if not msg or not msg.media:
            return False
        ttl = getattr(msg.media, "ttl_seconds", None) or getattr(msg.media, "ttl", None)
        return bool(ttl)

    async def save_message(evt):
        msg = evt.message
        chat_id = evt.chat_id
        msg_id = msg.id
        sender_id = msg.sender_id
        if bot_id is not None and sender_id == bot_id:
            return
        text = msg.message or ""
        date = msg.date.isoformat()
        media_path = await download_media_safe(msg, media_dir)
        try:
            sender = await evt.get_sender()
        except Exception:
            sender = None
        sender_display = await resolve_user_tag(sender, sender_id)

        cur.execute(
            """
            INSERT OR REPLACE INTO messages
            (chat_id, msg_id, sender_id, sender_display, date, text, media_path, deleted)
            VALUES (?, ?, ?, ?, ?, ?, ?, COALESCE((SELECT deleted FROM messages WHERE chat_id=? AND msg_id=?), 0))
            """,
            (chat_id, msg_id, sender_id, sender_display, date, text, media_path, chat_id, msg_id),
        )
        conn.commit()

        if is_view_once(msg):
            sender_tag = sender_display
            header = "View-once media"
            details = [
                header,
                f"sender: {sender_tag}",
                f"chat: {chat_id}",
            ]
            extra = text.strip()
            if extra:
                details.append(f"text: {extra}")
            caption = "\n".join(details)
            if media_path:
                await notifier.send_view_once(media_path, caption)
            else:
                await notifier.notify(f"{caption}\n(media unavailable)")

    async def save_edit(evt):
        msg = evt.message
        chat_id = evt.chat_id
        msg_id = msg.id
        sender_id = msg.sender_id
        if bot_id is not None and sender_id == bot_id:
            return
        new_text = msg.message or ""
        edit_date = datetime.utcnow().isoformat()

        cur.execute("SELECT text, media_path, sender_display FROM messages WHERE chat_id=? AND msg_id=?", (chat_id, msg_id))
        row = cur.fetchone()
        old_text, old_media, stored_sender = (row if row else (None, None, None))

        cur.execute(
            "INSERT INTO edits (chat_id, msg_id, edit_date, old_text, media_path) VALUES (?, ?, ?, ?, ?)",
            (chat_id, msg_id, edit_date, old_text, old_media),
        )
        cur.execute(
            "UPDATE messages SET text=?, date=? WHERE chat_id=? AND msg_id=?",
            (new_text, edit_date, chat_id, msg_id),
        )
        conn.commit()

        try:
            sender = await evt.get_sender()
        except Exception:
            sender = None
        sender_tag = await resolve_user_tag(sender, sender_id, stored_sender)
        old_block = format_text_block(old_text)
        new_block = format_text_block(new_text)
        message = (
            f"User {sender_tag} edited a message:\n\n"
            f"```{old_block}\n```\n"
            "to\n\n"
            f"```{new_block}\n```"
        )
        await notifier.notify(message)

    async def mark_deleted(evt):
        chat_id = evt.chat_id
        for msg_id in evt.deleted_ids:
            cur.execute(
                "SELECT sender_id FROM messages WHERE chat_id=? AND msg_id=?",
                (chat_id, msg_id),
            )
            row_sender = cur.fetchone()
            existing_sender_id = row_sender[0] if row_sender else None
            if bot_id is not None and existing_sender_id == bot_id:
                continue
            cur.execute(
                "SELECT text, sender_id, sender_display FROM messages WHERE chat_id=? AND msg_id=?",
                (chat_id, msg_id),
            )
            row = cur.fetchone()

            if row is None:
                cur.execute(
                    "SELECT text, sender_id, sender_display FROM messages WHERE msg_id=? ORDER BY rowid DESC LIMIT 1",
                    (msg_id,),
                )
                row = cur.fetchone()

            old_text, sender_id, stored_sender = (row if row else (None, None, None))
            fetched_text = None
            fetched_sender = None
            fetched_sender_id = None
            fetched_sender_display = None

            if row is None or old_text is None or stored_sender is None:
                try:
                    fetched_msg = await user_client.get_messages(chat_id, ids=msg_id)
                    if fetched_msg:
                        fetched_text = fetched_msg.message or None
                        fetched_sender_id = getattr(fetched_msg, "sender_id", None)
                        try:
                            fetched_sender = await fetched_msg.get_sender()
                        except Exception:
                            fetched_sender = None
                        fetched_sender_display = await resolve_user_tag(fetched_sender, fetched_sender_id)
                except Exception:
                    fetched_msg = None

            final_text = old_text if old_text is not None else fetched_text
            final_sender_id = sender_id or fetched_sender_id
            final_sender_display = stored_sender or fetched_sender_display

            if row:
                cur.execute(
                    "UPDATE messages SET deleted=1, sender_id=COALESCE(?, sender_id), sender_display=COALESCE(?, sender_display), text=COALESCE(text, ?) WHERE chat_id=? AND msg_id=?",
                    (final_sender_id, final_sender_display, final_text, chat_id, msg_id),
                )
            elif final_text is not None or final_sender_id is not None or final_sender_display is not None:
                cur.execute(
                    "INSERT OR IGNORE INTO messages (chat_id, msg_id, sender_id, sender_display, date, text, media_path, deleted) VALUES (?, ?, ?, ?, ?, ?, ?, 1)",
                    (chat_id, msg_id, final_sender_id, final_sender_display, datetime.utcnow().isoformat(), final_text, None),
                )

            old_block = format_text_block(final_text)
            sender_tag = await resolve_user_tag(fetched_sender, final_sender_id, final_sender_display)
            message = (
                f"User {sender_tag} deleted a message (id: {msg_id}):\n\n"
                f"```{old_block}```"
            )
            await notifier.notify(message)
        conn.commit()

    @user_client.on(events.NewMessage)
    async def handler_new(evt):
        try:
            await save_message(evt)
        except FloodWaitError as e:
            await asyncio.sleep(e.seconds)
        except Exception as e:
            await notifier.notify(f"[new] error: {e}")

    @user_client.on(events.MessageEdited)
    async def handler_edit(evt):
        try:
            await save_edit(evt)
        except FloodWaitError as e:
            await asyncio.sleep(e.seconds)
        except Exception as e:
            await notifier.notify(f"[edit] error: {e}")

    @user_client.on(events.MessageDeleted)
    async def handler_delete(evt):
        try:
            await mark_deleted(evt)
        except FloodWaitError as e:
            await asyncio.sleep(e.seconds)
        except Exception as e:
            await notifier.notify(f"[delete] error: {e}")