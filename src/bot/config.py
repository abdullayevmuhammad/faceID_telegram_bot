import os
import ast
from dotenv import load_dotenv

# .env faylni yuklaymiz
load_dotenv()

# ======================
# 🤖 Telegram Bot Sozlamalari
# ======================
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
print("ADMIN_ID:", ADMIN_ID, type(ADMIN_ID))
# ADMIN_ID: 2007357355 <class 'int'>

# ======================
# 🌐 FaceID API Sozlamalari
# ======================
FACEID_ENABLED = os.getenv("FACEID_ENABLED", "false").lower() == "true"
FACEID_USERNAME = os.getenv("FACEID_USERNAME", "admin")
FACEID_PASSWORD = os.getenv("FACEID_PASSWORD", "")
FACEID_AUTH_HEADER = os.getenv("FACEID_AUTH_HEADER", "")
FACEID_API_URL = os.getenv("FACEID_API_URL", "")

# 🧩 FACEID_HOSTS endi .env dagi Python list ko‘rinishidan o‘qiladi
try:
    FACEID_HOSTS = ast.literal_eval(os.getenv("FACEID_HOSTS", "[]"))
    if not isinstance(FACEID_HOSTS, list):
        raise ValueError("FACEID_HOSTS must be a list")
except Exception as e:
    print(f"⚠️ FACEID_HOSTS ni o‘qishda xato: {e}")
    FACEID_HOSTS = []

# ======================
# ⚙️ Umumiy sozlamalar
# ======================
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
