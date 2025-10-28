# src/bot/handlers/start.py
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from utils.db import is_admin
from bot.keyboards.main_menu import user_main_menu, admin_main_menu

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    """Boshlang‘ich menyu"""
    if is_admin(message.from_user.id):
        await message.answer(
            f"👋 Salom, {message.from_user.full_name}!\nSiz admin sifatida tizimga kirdingiz ✅",
            reply_markup=admin_main_menu()
        )
    else:
        await message.answer(
            f"👋 Salom, {message.from_user.full_name}!\nFaceID tizimiga xush kelibsiz!",
            reply_markup=user_main_menu()
        )
