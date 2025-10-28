import sqlite3
from datetime import datetime

conn = sqlite3.connect("src/db.sqlite")
cursor = conn.cursor()

telegram_id = 2007357355  # bu sening Telegram ID’ing bo‘lishi kerak
full_name = "Muhammad"
created_at = datetime.now().isoformat()

cursor.execute("""
INSERT INTO users (telegram_id, full_name, role, created_at)
VALUES (?, ?, 'admin', ?)
""", (telegram_id, full_name, created_at))

conn.commit()
conn.close()
print("✅ Admin foydalanuvchi muvaffaqiyatli qo‘shildi.")
