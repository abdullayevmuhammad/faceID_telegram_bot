from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from pathlib import Path
from utils.db import get_user_by_id, update_photo as update_db_photo
from utils.faceapi import update_face_photo_all
from bot.states.update_states import UpdateUser
from bot.keyboards.user_keyboards import cancel_keyboard, main_menu_keyboard

router = Router()
PHOTO_DIR = Path("tmp_photos")
PHOTO_DIR.mkdir(exist_ok=True)


@router.message(F.text == "🔄 Ma'lumotni yangilash")
async def start_update(message: Message, state: FSMContext):
    """Foydalanuvchi ma’lumotlarini yangilash (faqat rasm)"""
    user = get_user_by_id(message.from_user.id)

    if not user:
        return await message.answer("❌ Siz hali ro‘yxatdan o‘tmagansiz.\nAvval /register orqali ro‘yxatdan o‘ting.")

    passport = user["passport"]

    await message.answer(
        f"👤 <b>Profilingiz:</b>\n"
        f"🪪 Pasport: <b>{passport}</b>\n"
        f"👥 Ism: {user['full_name']}\n"
        f"📅 Ro‘yxatdan o‘tgan: {user['created_at'][:19]}\n\n"
        f"📸 Iltimos, yangi rasm yuboring (yoki ❌ Bekor qilish tugmasini bosing).",
        parse_mode="HTML",
        reply_markup=cancel_keyboard()
    )

    if user.get("photo_id"):
        await message.answer_photo(user["photo_id"])

    await state.update_data(passport=passport)
    await state.set_state(UpdateUser.waiting_for_photo)


@router.message(UpdateUser.waiting_for_photo, F.photo)
async def handle_photo(message: Message, state: FSMContext):
    """Foydalanuvchi yangi rasm yuborganda"""
    data = await state.get_data()
    passport = data.get("passport")

    if not passport:
        return await message.answer("⚠️ Xatolik: foydalanuvchi aniqlanmadi. Iltimos, qayta urinib ko‘ring.")

    file = await message.bot.get_file(message.photo[-1].file_id)
    photo_path = PHOTO_DIR / f"{passport}_{message.from_user.id}.jpg"
    await message.bot.download_file(file.file_path, destination=str(photo_path))

    await message.answer("⏳ Rasm barcha qurilmalarda yangilanmoqda...")

    resp = await update_face_photo_all(passport, str(photo_path))

    if resp.get("status") == "success":
        success_count = len([r for r in resp.get("details", []) if r.get("status") == "success"])
        await message.answer(
            f"✅ Rasm muvaffaqiyatli yangilandi!\n"
            f"📊 {success_count}/{len(resp.get('details', []))} qurilmada yangilandi.",
            reply_markup=main_menu_keyboard()
        )
        update_db_photo(message.from_user.id, message.photo[-1].file_id)
    else:
        await message.answer(
            "❌ Rasm yangilashda xato: " + resp.get("msg", "Noma’lum xato."),
            reply_markup=main_menu_keyboard()
        )

    try:
        photo_path.unlink()
    except Exception:
        pass

    await state.clear()
