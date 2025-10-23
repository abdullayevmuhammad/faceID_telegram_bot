from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from utils.db import get_user_by_id, is_user_registered
from bot.keyboards.user_keyboards import main_menu_keyboard
from bot.keyboards.main_menu import admin_main_menu  # ✅ TO‘G‘RI JOYDAN IMPORT
from bot.config import ADMIN_ID

router = Router()

@router.message(CommandStart())
async def start_command(message: Message):
    """Start — foydalanuvchini aniqlash va menyu ko‘rsatish"""
    user = get_user_by_id(message.from_user.id)

    # 👤 Foydalanuvchi topilmagan
    if not user:
        text = (
            f"Assalomu alaykum, {message.from_user.full_name}!\n\n"
            "Siz hali tizimda ro‘yxatdan o‘tmagansiz.\n"
            "Boshlash uchun 🪪 <b>Ro‘yxatdan o‘tish</b> tugmasini bosing 👇"
        )
        return await message.answer(text, parse_mode="HTML", reply_markup=main_menu_keyboard())

    # 👑 Agar foydalanuvchi bazada bor bo‘lsa
    role = user.get("role", "user")
    menu = admin_main_menu() if role == "admin" else main_menu_keyboard()

    # 🧾 To‘liq ro‘yxatdan o‘tganligini tekshirish
    if not is_user_registered(message.from_user.id):
        text = (
            f"👋 Salom, {message.from_user.full_name}!\n\n"
            "Siz ro‘yxatdan o‘tishni hali to‘liq yakunlamagansiz.\n"
            "Davom ettirish uchun 🪪 <b>Ro‘yxatdan o‘tish</b> tugmasini bosing."
        )
        return await message.answer(text, parse_mode="HTML", reply_markup=menu)

    # ✅ To‘liq ro‘yxatdan o‘tgan foydalanuvchi
    await message.answer(
        f"Assalomu alaykum, {message.from_user.full_name}!\n"
        "Siz tizimda ro‘yxatdan o‘tgan ekansiz ✅\n"
        "Quyidagi menyudan kerakli amalni tanlang 👇",
        reply_markup=menu
    )

