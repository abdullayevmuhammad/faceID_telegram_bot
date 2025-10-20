# src/bot/handlers/register_user.py
import os
from pathlib import Path
import re
from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from bot.states.register_states import RegisterUser
from utils.storage_db import user_storage_db
from utils.faceapi import send_to_faceid
import asyncio

router = Router()

PHOTOS_DIR = Path("tmp_photos")
PHOTOS_DIR.mkdir(exist_ok=True)


# 1️⃣ /register bosqichi
@router.message(Command("register"))
async def start_register(message: Message, state: FSMContext):
    await message.answer("🪪 Pasport seriyangizni kiriting: (masalan: AB1234567)")
    await state.set_state(RegisterUser.waiting_for_passport)


# 2️⃣ Pasport qabul qilish bosqichi
@router.message(RegisterUser.waiting_for_passport)
async def process_passport(message: Message, state: FSMContext):
    passport = message.text.strip().upper()

    if not re.match(r"^[A-Z]{2}\d{7}$", passport):
        await message.answer("❌ Noto‘g‘ri format! Masalan: AB1234567")
        return

    await state.update_data(passport=passport)
    await message.answer("✅ Pasport qabul qilindi! Endi rasm yuboring 📸")
    await state.set_state(RegisterUser.waiting_for_photo)


# 3️⃣ Rasm qabul qilish bosqichi
@router.message(RegisterUser.waiting_for_photo, F.photo)
async def process_photo(message: Message, state: FSMContext):
    user_data = await state.get_data()
    passport = user_data.get("passport")
    photo_id = message.photo[-1].file_id

    file = await message.bot.get_file(photo_id)
    local_path = PHOTOS_DIR / f"{passport}_{message.from_user.id}.jpg"
    await message.bot.download_file(file.file_path, destination=str(local_path))

    # Ma’lumotni DB ga saqlash
    user = await user_storage_db.add_or_update_user(
        telegram_id=message.from_user.id,
        full_name=message.from_user.full_name or "Unknown",
        passport=passport,
        photo_id=photo_id,
        photo_path=str(local_path)
    )

    # Tez javob
    await message.answer("📸 Rasm qabul qilindi! Ma'lumotlaringiz qayta ishlanmoqda...")

    # ✅ Fon rejimida FaceID yuborish
    task = asyncio.create_task(send_faceid_and_update_db(message, user, passport, local_path))

    def _task_done_callback(t: asyncio.Task):
        try:
            exc = t.exception()
            if exc:
                print("⚠️ Background task raised:", repr(exc))
        except asyncio.CancelledError:
            print("ℹ️ Background task cancelled")

    task.add_done_callback(_task_done_callback)

    await state.clear()


# 4️⃣ FaceID yuborish va holatni DBda yangilash
async def send_faceid_and_update_db(message: Message, user: dict, passport: str, local_path: Path):
    """Fon rejimida FaceID APIga yuborish va DB holatini yangilash"""
    try:
        api_resp = await send_to_faceid(passport, str(local_path))

        if api_resp.get("status") in ("success", "ok", True):
            await user_storage_db.update_status(
                user["id"], synced=True, faceid_status="ok"
            )
            await message.answer("✅ Siz tizimga muvaffaqiyatli qo'shildingiz!")
        else:
            await user_storage_db.update_status(
                user["id"], synced=False, faceid_status="error"
            )
            await message.answer("⚠️ FaceID serverida xatolik. Keyinroq qayta sinab ko‘riladi.")

    except Exception as e:
        print("❌ FaceID xatolik:", e)
        await user_storage_db.update_status(
            user["id"], synced=False, faceid_status="error"
        )
        await message.answer("⚠️ FaceID serveriga ulanishda xatolik. Keyinroq urinib ko‘ring.")

    # Faylni o‘chirish
    try:
        local_path.unlink(missing_ok=True)
    except Exception as e:
        print("⚠️ Faylni o‘chirishda xatolik:", e)
