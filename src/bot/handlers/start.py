# src/bot/handlers/start.py
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.utils.markdown import hbold, hitalic
from bot.keyboards.user_keyboards import main_menu_keyboard

router = Router()

@router.message(CommandStart())
async def start_handler(message: Message):
    user = message.from_user

    text = (
        f"👋 Salom, {hbold(user.first_name)}!\n\n"
        "🎯 <b>Face ID Tizimi</b> ga xush kelibsiz!\n\n"
        "Bu bot yordamida siz:\n"
        "✅ Ro'yxatdan o'tishingiz\n"
        "✅ Ma'lumotlaringizni yangilashingiz\n"
        "✅ Profilingizni ko'rishingiz mumkin\n\n"
        f"{hitalic('Quyidagi tugmalardan birini tanlang:')}"
    )

    await message.answer(text, reply_markup=main_menu_keyboard())