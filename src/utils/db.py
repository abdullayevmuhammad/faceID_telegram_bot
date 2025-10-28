import sqlite3
from typing import Optional, Dict, List

DB_PATH = "db.sqlite"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# =====================================================
# 🧱 Bazani yaratish
# =====================================================
def init_db():
    """Bazani yaratish (agar yo‘q bo‘lsa)"""
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        telegram_id INTEGER PRIMARY KEY,
        passport TEXT,
        full_name TEXT,
        username TEXT,
        role TEXT DEFAULT 'user',
        photo_id TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


# =====================================================
# 👤 Foydalanuvchilar
# =====================================================
def add_user(
    telegram_id: int,
    passport: str = "",
    full_name: str = "",
    username: str = "",
    role: str = "user",
    photo_id: str = None,
):
    """Yangi foydalanuvchi qo‘shish yoki yangilash"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT OR REPLACE INTO users (telegram_id, passport, full_name, username, role, photo_id)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (telegram_id, passport.upper(), full_name, username, role, photo_id))
    conn.commit()
    conn.close()


def get_user_by_id(telegram_id: int) -> Optional[Dict]:
    """Foydalanuvchini ID bo‘yicha olish"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def update_photo(telegram_id: int, new_photo_id: str):
    """Foydalanuvchi rasmini yangilash"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE users SET photo_id = ? WHERE telegram_id = ?", (new_photo_id, telegram_id))
    conn.commit()
    conn.close()


def is_user_registered(telegram_id: int) -> bool:
    """Foydalanuvchi ro‘yxatdan o‘tganmi"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT passport FROM users WHERE telegram_id = ?", (telegram_id,))
    result = cur.fetchone()
    conn.close()
    return bool(result and result["passport"])


# =====================================================
# 👑 Adminlar
# =====================================================
def is_admin(telegram_id: int) -> bool:
    """Adminligini tekshirish"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM users WHERE telegram_id = ? AND role = 'admin'", (telegram_id,))
    res = cur.fetchone()
    conn.close()
    return res is not None


def get_admins() -> List[Dict]:
    """Barcha adminlarni olish"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT telegram_id, username, full_name, created_at FROM users WHERE role = 'admin'")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def promote_to_admin(telegram_id: int):
    """Userni admin qilish"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE users SET role = 'admin' WHERE telegram_id = ?", (telegram_id,))
    conn.commit()
    conn.close()


def demote_admin(telegram_id: int):
    """Adminni oddiy userga qaytarish"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE users SET role = 'user' WHERE telegram_id = ?", (telegram_id,))
    conn.commit()
    conn.close()
