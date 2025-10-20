from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from bot.config import ADMIN_ID
from bot.keyboards.main_menu import user_main_menu, admin_main_menu

router = Router()

@router.message(CommandStart())
async def start_command(message: Message):
    """Start — foydalanuvchi turini aniqlaydi va menyu ko‘rsatadi"""
    if message.from_user.id == ADMIN_ID:
        menu = admin_main_menu()
        role = "👑 Admin"
    else:
        menu = user_main_menu()
        role = "👤 Foydalanuvchi"

    await message.answer(
        f"Assalomu alaykum, {message.from_user.full_name}!\n"
        f"Siz tizimda: <b>{role}</b>\n\n"
        "Quyidagi menyudan kerakli amalni tanlang 👇",
        reply_markup=menu
    )
