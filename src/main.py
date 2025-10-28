# src/main.py
import asyncio
import logging
from aiogram import Bot, Dispatcher
from bot.config import BOT_TOKEN, ADMIN_ID
from utils.db import init_db, get_user_by_id, add_user, promote_to_admin, is_admin
from bot.handlers import start, menu_actions, profile, update_photo, register_user, admin_panel
from utils.faceapi import test_api_connections

logging.basicConfig(level=logging.INFO)

async def on_startup(bot: Bot):
    """Bot ishga tushganda bajariladigan ishlar"""
    print("🚀 Bot ishga tushmoqda...")

    init_db()
    print("📦 Database tayyor")

    # 👑 Super adminni tekshirish yoki yaratish
    admin = get_user_by_id(ADMIN_ID)
    if not admin:
        add_user(ADMIN_ID, passport="", full_name="Super Admin",  role="admin")
        print(f"👑 ADMIN_ID={ADMIN_ID} qo‘shildi (admin sifatida).")
    elif admin.get("role") != "admin":
        promote_to_admin(ADMIN_ID)
        print(f"🔁 ADMIN_ID={ADMIN_ID} admin qilib yangilandi.")
    else:
        print("✅ Super admin allaqachon mavjud.")

    # 🌐 API test
    test_result = await test_api_connections()
    print(f"🌐 API test natijasi: {test_result}")

    print("✅ Bot ishga tayyor!")

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Routerni ulash
    dp.include_router(start.router)
    dp.include_router(menu_actions.router)
    dp.include_router(profile.router)
    dp.include_router(update_photo.router)
    dp.include_router(register_user.router)
    dp.include_router(admin_panel.router)

    # Ishga tushirish
    await on_startup(bot)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("🛑 Bot to‘xtatildi")
