# src/bot/handlers/start.py
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.utils.markdown import hbold, hitalic

router = Router()

@router.message(CommandStart())
async def start_handler(message: Message):
    user = message.from_user

    text = (
        f"👋 Salom, {hbold(user.first_name)}!\n\n"
        "Bu Face ID tizimi uchun ro‘yxatdan o‘tish botidir.\n"
        "📸 Iltimos, quyidagi ma’lumotlarni yuboring:\n"
        "1️⃣ Pasport seriya raqamingiz (masalan: AD1234567)\n"
        "2️⃣ Yuzingizning aniq rasmi\n\n"
        f"{hitalic('Tizim sizni tanib olish uchun ushbu ma’lumotlardan foydalanadi.')}"
    )

    await message.answer(text)
