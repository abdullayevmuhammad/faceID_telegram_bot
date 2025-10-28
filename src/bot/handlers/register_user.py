from utils.db import add_user, get_user_by_id, is_user_registered
import asyncio
import re
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from bot.states.register_states import RegisterUser
from bot.keyboards.user_keyboards import cancel_keyboard, main_menu_keyboard
from bot.keyboards.admin_keyboards import admin_main_keyboard
from utils.faceapi import (
    find_user_in_all_devices,
    send_to_faceid,
    update_face_photo_all,
    copy_user_to_missing_devices,
    FACEID_HOSTS
)
from pathlib import Path

from bot.keyboards.main_menu import admin_main_menu, user_main_menu
from utils.db import is_admin

from bot.keyboards.main_menu import get_main_menu

router = Router()
PHOTO_DIR = Path("tmp_photos")
PHOTO_DIR.mkdir(exist_ok=True)


def get_choice_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Ha, rasm yangilash")],
            [KeyboardButton(text="❌ Yo'q, faqat ma'lumotlarni ko'chirish")]
        ],
        resize_keyboard=True
    )


# ======================
# /register komandasi
# ======================
@router.message(Command("register"))
async def start_register(message: Message, state: FSMContext):
    """Ro‘yxatdan o‘tishni boshlash"""
    user = get_user_by_id(message.from_user.id)

    # Agar user DB’da bor bo‘lsa, FaceID’da ham borligini tekshiramiz
    if user and user.get("passport"):
        passport = user["passport"]
        check = await find_user_in_all_devices(passport)

        if check["status"] == "found":
            # 🔹 FaceID tizimida ham bor
            return await message.answer(
                "✅ Siz allaqachon ro‘yxatdan o‘tgan ekansiz.\n"
                "Profilingizni ko‘rish uchun 👤 <b>Profilim</b> tugmasini bosing.",
                parse_mode="HTML",
                reply_markup=get_main_menu(message.from_user.id)
            )
        else:
            # 🔹 DB’da bor, lekin FaceID’da topilmadi → qayta ro‘yxatdan o‘tadi
            await state.clear()
            await message.answer(
                "⚠️ Sizning ma’lumotlaringiz FaceID tizimida topilmadi.\n"
                "Iltimos, qayta ro‘yxatdan o‘ting. Ilitmos, passport ID yuboring.",
                reply_markup=cancel_keyboard()
            )
            await state.set_state(RegisterUser.waiting_for_passport)
            return

    # Umuman yo‘q bo‘lsa — yangi foydalanuvchi
    await message.answer("🪪 Pasport raqamingizni kiriting:", reply_markup=cancel_keyboard())
    await state.set_state(RegisterUser.waiting_for_passport)


# ======================
# Pasport qabul qilish
# ======================
@router.message(RegisterUser.waiting_for_passport)
async def handle_passport(message: Message, state: FSMContext):
    passport = message.text.strip().upper()
    if not re.match(r"^[A-Z]{2}\d{7}$", passport):
        return await message.answer("❌ Noto'g'ri format! Masalan: <b>AB1234567</b>", parse_mode="HTML")

    await message.answer("🔍 Tizimda tekshirilmoqda...")
    result = await find_user_in_all_devices(passport)

    if result["status"] == "found":
        found_devices = result["devices"]
        found_count = len(found_devices)
        missing_hosts = [h for h in FACEID_HOSTS if h not in [d["host"] for d in found_devices]]

        if missing_hosts:
            asyncio.create_task(copy_user_to_missing_devices(passport))

        await message.answer(
            f"⚠️ <b>{passport}</b> tizimda mavjud!\n"
            f"📍 {found_count} ta qurilmada topildi\n\n"
            f"Rasmingizni yangilash yoki ma’lumotlarni boshqa qurilmalarga ko‘chirishni tanlang:",
            parse_mode="HTML",
            reply_markup=get_choice_keyboard()
        )
        await state.update_data(passport=passport, is_existing_user=True, found_devices=found_devices)
        await state.set_state(RegisterUser.waiting_for_update_choice)
    else:
        await message.answer("✅ Yangi foydalanuvchi. Iltimos, rasm yuboring 📸")
        await state.update_data(passport=passport, is_existing_user=False)
        await state.set_state(RegisterUser.waiting_for_photo)


# ======================
# Tanlov: yangilash yoki ko‘chirish
# ======================
@router.message(RegisterUser.waiting_for_update_choice,
                F.text.in_(["✅ Ha, rasm yangilash", "❌ Yo'q, faqat ma'lumotlarni ko'chirish"]))
async def handle_update_choice(message: Message, state: FSMContext):
    data = await state.get_data()
    passport = data["passport"]
    found_devices = data.get("found_devices", [])

    if message.text == "✅ Ha, rasm yangilash":
        await message.answer("📸 Iltimos, yangi rasm yuboring:", reply_markup=cancel_keyboard())
        await state.set_state(RegisterUser.waiting_for_photo)
        await state.update_data(is_existing_user=True)
    else:
        await message.answer("⏳ Ma'lumotlar barcha qurilmalarga ko'chirilmoqda...")
        result = await copy_user_to_missing_devices(passport)

        if result["status"] == "success":
            success_count = len([r for r in result.get("details", []) if r.get("status") == "success"])
            total_missing = len([h for h in FACEID_HOSTS if h not in [d["host"] for d in found_devices]])

            if total_missing == 0:
                msg = f"✅ Barcha {len(FACEID_HOSTS)} ta qurilmada ma'lumotlar mavjud."
            else:
                msg = f"✅ {success_count}/{total_missing} qurilmaga ma'lumot ko'chirildi."
            await message.answer(msg)
        else:
            await message.answer(f"❌ Xatolik: {result.get('msg', 'Maʼlumotlarni koʼchirishda xatolik')}")

        await state.clear()


# ======================
# Rasm yuborish
# ======================
@router.message(RegisterUser.waiting_for_photo, F.photo)
async def handle_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    passport = data["passport"]
    is_existing_user = data.get("is_existing_user", False)

    file = await message.bot.get_file(message.photo[-1].file_id)
    photo_path = PHOTO_DIR / f"{passport}_{message.from_user.id}.jpg"
    await message.bot.download_file(file.file_path, destination=str(photo_path))

    await message.answer("⏳ Ma'lumotlar barcha qurilmalarga yuborilmoqda...")

    if is_existing_user:
        resp = await update_face_photo_all(passport, str(photo_path))
        action = "yangilandi"
    else:
        resp = await send_to_faceid(passport, str(photo_path))
        action = "qo‘shildi"

    if resp.get("status") == "success":
        success_count = len([r for r in resp.get("details", []) if r.get("status") == "success"])
        await message.answer(
            f"✅ Ma'lumotlar muvaffaqiyatli {action}!\n"
            f"📊 {success_count}/{len(FACEID_HOSTS)} qurilmada {action}.",
            parse_mode="HTML",
            reply_markup=get_main_menu(message.from_user.id),
        )

        add_user(
            telegram_id=message.from_user.id,
            passport=passport,
            full_name=message.from_user.full_name,
            photo_id=message.photo[-1].file_id
        )
    else:
        await message.answer(f"⚠️ Xatolik: {resp.get('msg', 'Aniqlanmagan xato')}", parse_mode="HTML")

    try:
        photo_path.unlink()
    except Exception:
        pass

    await state.clear()
