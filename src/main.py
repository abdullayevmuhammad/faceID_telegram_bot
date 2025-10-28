# src/main.py
import asyncio
import logging
from aiogram import Bot, Dispatcher
from bot.config import BOT_TOKEN, ADMIN_ID
from bot.handlers import admin_edit_user
from utils.db import init_db, get_user_by_id, add_user, promote_to_admin, is_admin
from bot.handlers import start, menu_actions, profile, update_photo, register_user, admin_panel
from utils.faceapi import test_api_connections

logging.basicConfig(level=logging.INFO)





async def on_startup(bot: Bot):
    """Bot ishga tushganda bajariladigan ishlar"""
    print("🚀 Bot ishga tushmoqda...")

    init_db()
    print("📦 Database tayyor")
    # await clear_all_commands(bot)
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
    dp.include_router(admin_edit_user.router)

    # Ishga tushirish
    await on_startup(bot)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("🛑 Bot to‘xtatildi")


from aiogram.types import (
    BotCommandScopeAllPrivateChats,
    BotCommandScopeAllGroupChats,
    BotCommandScopeAllChatAdministrators,
    BotCommandScopeDefault,
    BotCommandScopeChat,
)

from utils.db import get_admins, get_all_users
from bot.config import ADMIN_ID

# async def clear_all_commands(bot):
#     """Botdagi barcha komandalarni tozalash (butunlay)"""
#     print("🧹 Barcha komandalar o‘chirilyapti...")
#
#     scopes = [
#         BotCommandScopeAllPrivateChats(),
#         BotCommandScopeAllGroupChats(),
#         BotCommandScopeAllChatAdministrators(),
#         BotCommandScopeDefault(),
#     ]
#
#     # 🔹 Global scope’lar
#     for scope in scopes:
#         try:
#             await bot.delete_my_commands(scope=scope)
#             print(f"✅ Global scope: {scope.__class__.__name__} tozalandi")
#         except Exception as e:
#             print(f"⚠️ {scope.__class__.__name__} tozalashda xatolik: {e}")
#
#     # 🔹 Super admin
#     try:
#         await bot.delete_my_commands(scope=BotCommandScopeChat(chat_id=ADMIN_ID))
#         print(f"✅ Super admin uchun komandalar o‘chirildi ({ADMIN_ID})")
#     except Exception as e:
#         print(f"⚠️ Super admin komandalarini o‘chirishda xatolik: {e}")
#
#     # 🔹 Barcha adminlar
#     try:
#         for adm in get_admins():
#             await bot.delete_my_commands(scope=BotCommandScopeChat(chat_id=adm["telegram_id"]))
#             print(f"✅ Admin komandalar o‘chirildi: {adm['telegram_id']}")
#     except Exception as e:
#         print(f"⚠️ Adminlar komandalarini o‘chirishda xatolik: {e}")
#
#     # 🔹 Barcha foydalanuvchilar
#     try:
#         for user in get_all_users():  # <-- db.py ga get_all_users() funksiyasini qo‘shamiz
#             await bot.delete_my_commands(scope=BotCommandScopeChat(chat_id=user["telegram_id"]))
#         print("✅ Barcha foydalanuvchilar uchun komandalar tozalandi.")
#     except Exception as e:
#         print(f"⚠️ User komandalarini tozalashda xatolik: {e}")
#
#     print("🧹 Komandalar butunlay o‘chirildi.\n")
