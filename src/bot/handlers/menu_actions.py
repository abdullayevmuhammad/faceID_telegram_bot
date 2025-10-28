# src/bot/handlers/menu_actions.py
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from bot.handlers import register_user, profile, update_photo, admin_panel
from utils.db import get_user_by_id
from bot.config import ADMIN_ID

router = Router()


# 🪪 Ro‘yxatdan o‘tish
@router.message(F.text.in_(["🪪 Ro'yxatdan o'tish", "📝 Ro'yxatdan o'tish"]))
async def button_register(message: Message, state: FSMContext):
    await register_user.start_register(message, state)


# 👤 Profilim
@router.message(F.text.in_(["👤 Profilim", "👤 Mening profilim"]))
async def button_profile(message: Message):
    await profile.profile_cmd(message)


# 🔄 Ma’lumotni yangilash
@router.message(F.text == "🔄 Ma'lumotni yangilash")
async def button_update(message: Message, state: FSMContext):
    await update_photo.start_update(message, state)


# 📊 Admin panel
@router.message(F.text == "📊 Admin panel")
async def button_admin(message: Message):
    """Faqat adminlar kira oladi"""
    user = get_user_by_id(message.from_user.id)

    # Asosiy admin yoki role=admin bo‘lsa ruxsat
    if message.from_user.id == ADMIN_ID or (user and user.get("role") == "admin"):
        await admin_panel.show_admin_panel(message)
    else:
        await message.answer("🚫 Sizda admin panelga kirish huquqi yo‘q.")


# ℹ️ Yordam
@router.message(F.text == "ℹ️ Yordam")
async def button_help(message: Message):
    await message.answer(
        "ℹ️ <b>Yordam:</b>\n\n"
        "🪪 Ro‘yxatdan o‘tish — pasport va rasm yuborish orqali tizimga kirish.\n"
        "👤 Profilim — o‘zingiz haqidagi ma’lumotni ko‘rish.\n"
        "🔄 Ma’lumotni yangilash — faqat rasmni yangilash.\n"
        "📊 Admin panel — faqat administratorlar uchun.\n\n"
        "Savollar bo‘lsa: @admin bilan bog‘laning.",
        parse_mode="HTML"
    )
