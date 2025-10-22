import re
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from bot.states.register_states import RegisterUser
from utils.faceapi import find_user_in_all_devices, send_to_faceid, update_face_photo_all
from bot.keyboards.user_keyboards import cancel_keyboard
from pathlib import Path

import random

router = Router()
PHOTO_DIR = Path("tmp_photos")
PHOTO_DIR.mkdir(exist_ok=True)


@router.message(Command("register"))
async def start_register(message: Message, state: FSMContext):
    await message.answer("🪪 Pasport raqamingizni kiriting (masalan: AB1234567):")
    await state.set_state(RegisterUser.waiting_for_passport)


@router.message(RegisterUser.waiting_for_passport)
async def handle_passport(message: Message, state: FSMContext):
    passport = message.text.strip().upper()
    if not re.match(r"^[A-Z]{2}\d{7}$", passport):
        return await message.answer("❌ Noto‘g‘ri format! Masalan: <b>AB1234567</b>", parse_mode="HTML")

    await message.answer("🔍 Tizimda tekshirilmoqda...")

    result = await find_user_in_all_devices(passport)
    if result["status"] == "found":
        devices = result.get("devices", [])
        device_list_str = "\n".join(f"📍 {d['host']} | 🆔 {d['uid']}" for d in devices)
        await message.answer(
            f"⚠️ <b>{passport}</b> allaqachon tizimda mavjud!\n\n"
            f"{device_list_str}\n\n"
            "Siz faqat rasmni yangilashingiz mumkin. Davom etasizmi?",
            parse_mode="HTML",
            reply_markup=cancel_keyboard()
        )
        await state.update_data(passport=passport)
        await state.set_state(RegisterUser.waiting_for_photo)
    else:
        await message.answer("✅ Yangi foydalanuvchi. Iltimos, rasm yuboring 📸")
        await state.update_data(passport=passport)
        await state.set_state(RegisterUser.waiting_for_photo)


@router.message(RegisterUser.waiting_for_photo, F.photo)
async def handle_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    passport = data["passport"]

    file = await message.bot.get_file(message.photo[-1].file_id)
    photo_path = PHOTO_DIR / f"{passport}_{message.from_user.id}.jpg"
    await message.bot.download_file(file.file_path, destination=str(photo_path))

    await message.answer("⏳ Rasm FaceID serverga yuborilmoqda...")

    # Tekshiruv: mavjud foydalanuvchi yoki yangi
    result = await find_user_in_all_devices(passport)
    if result["status"] == "found":
        # Mavjud foydalanuvchi → barcha qurilmalar uchun rasm yangilash
        resp = await update_face_photo_all(passport, str(photo_path))
    else:
        # Yangi foydalanuvchi → barcha qurilmalarga qo‘shish
        resp = await send_to_faceid(passport, str(photo_path))

    if resp.get("status") == "success":
        await message.answer(f"✅ Ma’lumotlar muvaffaqiyatli saqlandi!\n{resp.get('msg')}")
    else:
        await message.answer(f"⚠️ Xatolik: {resp.get('msg', 'unknown')}")

    await state.clear()
