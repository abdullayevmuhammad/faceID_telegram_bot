# src/bot/handlers/register_user.py
import re
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from bot.states.register_states import RegisterUser
# from src.database.session import async_session
from database.models import User
from datetime import datetime
from database.session import AsyncSessionLocal


router = Router()

# /register komandasi
@router.message(Command("register"))
async def start_register(message: Message, state: FSMContext):
    await message.answer("🪪 Pasport seriya raqamingizni kiriting (masalan: AB1234567):")
    await state.set_state(RegisterUser.waiting_for_passport)


# 1️⃣ Pasport seriyasini tekshirish
@router.message(RegisterUser.waiting_for_passport)
async def process_passport(message: Message, state: FSMContext):
    passport = message.text.strip().upper()

    if not re.match(r"^[A-Z]{2}\d{7}$", passport):
        await message.answer("❌ Noto‘g‘ri format. To‘g‘ri format: AB1234567")
        return

    await state.update_data(passport=passport)
    await message.answer("✅ Qabul qilindi! Endi yuzingizning aniq rasmni yuboring 📸")
    await state.set_state(RegisterUser.waiting_for_photo)


# 2️⃣ Rasmni qabul qilish va bazaga yozish
@router.message(RegisterUser.waiting_for_photo, F.photo)
async def process_photo(message: Message, state: FSMContext):
    user_data = await state.get_data()
    passport = user_data.get("passport")
    photo_id = message.photo[-1].file_id

    async with AsyncSessionLocal() as session:
        # Foydalanuvchi mavjudmi?
        existing = await session.get(User, message.from_user.id)
        if existing:
            existing.passport = passport
            existing.photo_id = photo_id
            existing.updated_at = datetime.utcnow()
        else:
            new_user = User(
                telegram_id=message.from_user.id,
                full_name=message.from_user.full_name,
                passport=passport,
                photo_id=photo_id,
                created_at=datetime.utcnow(),
            )
            session.add(new_user)
        await session.commit()

    await message.answer(
        f"✅ Ma’lumotlar saqlandi!\n\n"
        f"📄 Pasport: <b>{passport}</b>\n"
        f"🖼️ Rasm ID: <code>{photo_id}</code>\n\n"
        "Tizimga qo‘shildingiz ✅"
    )

    await state.clear()


@router.message(RegisterUser.waiting_for_photo)
async def wrong_photo_format(message: Message):
    await message.answer("❌ Iltimos, rasm yuboring (matn emas).")
