import sqlite3
from datetime import datetime

DB_PATH = "db.sqlite"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        telegram_id INTEGER PRIMARY KEY,
        passport TEXT,
        full_name TEXT,
        photo_id TEXT,
        role TEXT DEFAULT 'user',
        created_at TEXT
    )
    """)
    conn.commit()
    conn.close()


def add_user(telegram_id: int, passport: str, full_name: str, photo_id: str = None, role: str = "user"):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO users (telegram_id, passport, full_name, photo_id, role, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (telegram_id, passport.upper(), full_name, photo_id, role, datetime.now().isoformat()))

    conn.commit()
    conn.close()


def get_user_by_id(telegram_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT passport, full_name, photo_id, role, created_at FROM users WHERE telegram_id = ?", (telegram_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "passport": row[0],
            "full_name": row[1],
            "photo_id": row[2],
            "role": row[3],
            "created_at": row[4],
        }
    return None


def update_photo(telegram_id: int, new_photo_id: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET photo_id = ?, created_at = ? WHERE telegram_id = ?",
                   (new_photo_id, datetime.now().isoformat(), telegram_id))
    conn.commit()
    conn.close()

def get_admins():
    """Barcha adminlarni qaytaradi"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT telegram_id, full_name, created_at FROM users WHERE role = 'admin'")
    rows = cursor.fetchall()
    conn.close()
    return [
        {"telegram_id": r[0], "full_name": r[1], "created_at": r[2]} for r in rows
    ]


def promote_to_admin(telegram_id: int):
    """Foydalanuvchini admin qiladi"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET role = 'admin' WHERE telegram_id = ?", (telegram_id,))
    conn.commit()
    conn.close()


def demote_admin(telegram_id: int):
    """Adminni oddiy foydalanuvchiga aylantiradi"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET role = 'user' WHERE telegram_id = ?", (telegram_id,))
    conn.commit()
    conn.close()

def is_user_registered(telegram_id: int) -> bool:
    """Foydalanuvchi ro‘yxatdan o‘tganmi? — pasport mavjudligiga qarab"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT passport FROM users WHERE telegram_id = ?", (telegram_id,))
    result = cursor.fetchone()
    conn.close()
    return bool(result and result[0])  # True agar passport mavjud bo‘lsa
