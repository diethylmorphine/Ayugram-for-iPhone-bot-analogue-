import sqlite3


def init_db(path: str = "messages.db"):
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (
            chat_id INTEGER,
            msg_id INTEGER,
            sender_id INTEGER,
            sender_display TEXT,
            date TEXT,
            text TEXT,
            media_path TEXT,
            deleted INTEGER DEFAULT 0,
            PRIMARY KEY (chat_id, msg_id)
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS edits (
            chat_id INTEGER,
            msg_id INTEGER,
            edit_date TEXT,
            old_text TEXT,
            media_path TEXT
        )
        """
    )
    try:
        cur.execute("ALTER TABLE messages ADD COLUMN sender_display TEXT")
        conn.commit()
    except sqlite3.OperationalError:
        pass

    conn.commit()
    return conn