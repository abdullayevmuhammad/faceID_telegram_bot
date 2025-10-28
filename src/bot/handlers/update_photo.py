# src/bot/handlers/update_photo.py
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from pathlib import Path
from utils.db import get_user_by_id, update_photo as update_db_photo
from utils.faceapi import find_user_in_all_devices, update_face_photo_all, FACEID_HOSTS, copy_user_to_missing_devices
from bot.states.update_states import UpdateUser
from bot.keyboards.user_keyboards import cancel_keyboard, main_menu_keyboard

from bot.keyboards.main_menu import admin_main_menu

from utils.db import is_admin

from bot.keyboards.main_menu import user_main_menu

from bot.keyboards.main_menu import get_main_menu

router = Router()
PHOTO_DIR = Path("tmp_photos")
PHOTO_DIR.mkdir(exist_ok=True)


@router.message(F.text == "🔄 Ma'lumotni yangilash")
async def start_update(message: Message, state: FSMContext):
    """Foydalanuvchi faqat rasmni yangilaydi"""
    user = get_user_by_id(message.from_user.id)
    if not user or not user.get("passport"):
        return await message.answer("❌ Siz hali ro‘yxatdan o‘tmagansiz.\nAvval 🪪 Ro‘yxatdan o‘ting.")

    passport = user["passport"]
    await message.answer(
        f"📸 <b>{passport}</b> uchun yangi rasm yuboring.\n"
        f"(Yoki ❌ Bekor qilish tugmasini bosing.)",
        parse_mode="HTML",
        reply_markup=cancel_keyboard()
    )

    await state.update_data(passport=passport)
    await state.set_state(UpdateUser.waiting_for_photo)


@router.message(UpdateUser.waiting_for_photo, F.photo)
async def handle_photo(message: Message, state: FSMContext):
    """Foydalanuvchi yangi rasm yuboradi — barcha APIlarda yangilanadi"""
    data = await state.get_data()
    passport = data.get("passport")

    if not passport:
        return await message.answer("⚠️ Xatolik: foydalanuvchi aniqlanmadi. Iltimos, qayta urinib ko‘ring.")

    file = await message.bot.get_file(message.photo[-1].file_id)
    photo_path = PHOTO_DIR / f"{passport}_{message.from_user.id}.jpg"
    await message.bot.download_file(file.file_path, destination=str(photo_path))

    await message.answer("⏳ Yangi rasm barcha qurilmalarda yangilanmoqda...")

    # Avval foydalanuvchi barcha APIlarda borligiga ishonch hosil qilamiz
    result = await find_user_in_all_devices(passport)
    if result["status"] != "found" or not result["devices"]:
        return await message.answer(f"⚠️ {passport} tizimda topilmadi. Avval ro‘yxatdan o‘ting.")

    found_hosts = [d["host"] for d in result["devices"]]
    missing_hosts = [h for h in FACEID_HOSTS if h not in found_hosts]

    # Sinxronizatsiya — ba'zi qurilmalarda foydalanuvchi yo‘q bo‘lsa
    if missing_hosts:
        await message.answer("🔄 Ba’zi qurilmalarda foydalanuvchi topilmadi. Sinxronizatsiya qilinmoqda...")
        await copy_user_to_missing_devices(passport)

    # Endi barcha APIlarda rasmni yangilaymiz
    resp = await update_face_photo_all(passport, str(photo_path))

    if resp.get("status") == "success":
        success_count = len([r for r in resp.get("details", []) if r.get("status") == "success"])
        await message.answer(
            f"✅ Rasm muvaffaqiyatli yangilandi!\n"
            f"📊 {success_count}/{len(FACEID_HOSTS)} qurilmada yangilandi.",
            reply_markup=get_main_menu(message.from_user.id)
        )
        update_db_photo(message.from_user.id, message.photo[-1].file_id)
    else:
        await message.answer(
            f"❌ Xatolik: {resp.get('msg', 'Rasm yangilashda muammo')}",
            reply_markup=get_main_menu(message.from_user.id)
        )

    try:
        photo_path.unlink()
    except Exception:
        pass

    await state.clear()

# ❌ Bekor qilish tugmasi
@router.message(F.text.in_(["❌ Bekor qilish", "❌ Bekor"]))
async def cancel_update(message: Message, state: FSMContext):
    """Rasm yangilash jarayonini bekor qiladi"""
    await state.clear()
    await message.answer("❌ Bekor qilindi.", reply_markup=get_main_menu(message.from_user.id))

