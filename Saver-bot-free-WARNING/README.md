## # Ayugram-for-iPhone (bot analogue) FREE VERSION

An analog of the Ayugram (Exteragram) app for iPhone users 

## Features
- Persist messages, edits, and deletions into `messages.db` (SQLite).
- View-once media capture: downloads media before it disappears and forwards it with context.
- Edit notifications: shows old vs new text in code blocks.
- Delete notifications: shows original text and message id (when available).
- Media saving to a configurable directory.

## Requirements
- Python 3.10+ (project uses a virtual environment in examples).
- Telegram API credentials from https://my.telegram.org (API ID & hash).
- A bot token from BotFather for the notifier bot.
- An admin user ID to receive notifications.

## Configuration
All settings are read from environment variables with defaults matching `config.py`.

| Variable | Description
| --- | ---
| `TG_API_ID` | Telegram API ID
| `TG_API_HASH` | Telegram API hash
| `TG_SESSION` | User session name/file
| `MEDIA_DIR` | Directory for downloaded media
| `TG_BOT_TOKEN` | Bot token for notifier
| `TG_BOT_ID` | Bot user ID (to ignore self messages)
| `TG_ADMIN_ID` | Admin user ID to receive notifications

> Replace defaults with your own secrets before deploying.

## Setup
1. Install dependencies (Telethon):
   ```bash
   pip install telethon
   ```
2. Setup variables in **config.py**


## Running
```bash
source .venv/bin/activate
python bot.py
```
On first run, Telethon will create/ask for `TG_SESSION` (user auth). The notifier bot will message the admin when the userbot starts.

## How it works
- `bot.py`: initializes DB, starts user client + notifier bot, registers handlers, and runs until disconnected.
- `handlers.py`:
  - New message: stores text/media in SQLite; if view-once, downloads media and forwards to admin.
  - Edit: logs old text in `edits` table and notifies admin with old/new blocks.
  - Delete: marks message as deleted; tries to reuse stored text/sender or fetches by `msg_id`; notifies admin with text and message id.
  - Self-filter: messages from `BOT_ID` are ignored for new/edit; deletes skip records whose sender matches `BOT_ID`.
- `notifier.py`: sends text or files to the admin bot chat.
- `db.py`: creates `messages` and `edits` tables (adds `sender_display` column if missing).
- `media.py`: safe media download helper.

## Database schema (messages)
- `chat_id`, `msg_id` (PK)
- `sender_id`, `sender_display`
- `date`
- `text`
- `media_path`
- `deleted` (0/1)

`edits` table keeps a history of edits with `old_text` and `edit_date`.

## Notifications format
- View-once: sender, chat, optional text; media forwarded when saved.
- Edit: `User <name> edited a message:` then old/new blocks.
- Delete: `User <name> deleted a message (id: <msg_id>):` then original text block.

## Media storage
- Files saved to `MEDIA_DIR` (created if absent). Paths are recorded in `messages.media_path`.

## Tips & troubleshooting
- If you see placeholders (`<unknown>` / `<data unavailable>`), Telegram didn't return the info and it wasn't stored earlier.
- Ensure `TG_BOT_ID` matches the notifier bot's user ID so self-messages are filtered.
- Run with `python bot.py` from the project root so relative paths (DB, media dir) resolve correctly.
- To inspect DB quickly:
  ```bash
  sqlite3 messages.db "SELECT chat_id,msg_id,sender_display,text,deleted FROM messages ORDER BY rowid DESC LIMIT 5;"
  ```

## Security
- Keep API keys, tokens, and session files private.
- Restrict filesystem access to `messages.db` and `MEDIA_DIR`.

## WARNING

# The author is not responsible for any consequences of using this bot; according to some reports, it violates Telegram's ToS.
# The author is not responsible for any consequences of using this bot; according to some reports, it violates Telegram's ToS.
# The author is not responsible for any consequences of using this bot; according to some reports, it violates Telegram's ToS.
# The author is not responsible for any consequences of using this bot; according to some reports, it violates Telegram's ToS.
# The author is not responsible for any consequences of using this bot; according to some reports, it violates Telegram's ToS.

## License
In LICENSE file
