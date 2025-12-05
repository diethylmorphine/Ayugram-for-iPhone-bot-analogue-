import os

API_ID = int(os.getenv("TG_API_ID", "")) # my.telegram.org
API_HASH = os.getenv("TG_API_HASH", "") # my.telegram.org
SESSION = os.getenv("TG_SESSION", "my_session") # session file name | creates a new one if it doesn't exist
MEDIA_DIR = os.getenv("MEDIA_DIR", "") # directory to save downloaded media

BOT_TOKEN = os.getenv("TG_BOT_TOKEN", "") # bot token from BotFather
BOT_ID = int(os.getenv("TG_BOT_ID", "")) # bot user ID
ADMIN_ID = int(os.getenv("TG_ADMIN_ID", "")) # admin user ID
