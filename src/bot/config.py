# src/bot/config.py
import os
from dotenv import load_dotenv

load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN", "8363824683:AAEzNvWQox8ALDQI3MKemZVpK3IvGNhtfgE")

# Admin Configuration
ADMIN_ID = int(os.getenv("ADMIN_ID", "2007357355"))

# Face ID API Configuration (for future use)
FACEID_API_URL = os.getenv("FACEID_API_URL", "http://192.168.15.20/webs/getWhitelist")
FACEID_USERNAME = os.getenv("FACEID_USERNAME", "admin")
FACEID_PASSWORD = os.getenv("FACEID_PASSWORD", "aifu1q2w3e4r@")