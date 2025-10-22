from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from pathlib import Path
from utils.faceapi import find_user_in_all_devices, update_face_photo_all
from bot.states.update_states import UpdateUser
from bot.keyboards.user_keyboards import cancel_keyboard

router = Router()
PHOTO_DIR = Path("tmp_photos")
PHOTO_DIR.mkdir(exist_ok=True)


@router.message(Command("update"))
async def start_update(message: Message, state: FSMContext):
    await message.answer("🪪 Pasport raqamingizni kiriting (rasmni yangilash uchun):")
    await state.set_state(UpdateUser.waiting_for_passport)


@router.message(UpdateUser.waiting_for_passport)
async def handle_passport(message: Message, state: FSMContext):
    passport = message.text.strip().upper()
    result = await find_user_in_all_devices(passport)

    if result["status"] == "not_found":
        await message.answer("❌ Bunday foydalanuvchi tizimda topilmadi.")
        return await state.clear()

    await message.answer(
        f"✅ Topildi!\n📍 Qurilma: <code>{result['device']}</code>\n🆔 UID: <code>{result['uid']}</code>\n\n"
        "📸 Endi yangi rasm yuboring:",
        parse_mode="HTML"
    )
    await state.update_data(passport=passport, device=result["device"])
    await state.set_state(UpdateUser.waiting_for_photo)


@router.message(UpdateUser.waiting_for_photo, F.photo)
async def handle_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    passport = data["passport"]
    device = data["device"]

    file = await message.bot.get_file(message.photo[-1].file_id)
    photo_path = PHOTO_DIR / f"{passport}_{message.from_user.id}.jpg"
    await message.bot.download_file(file.file_path, destination=str(photo_path))

    await message.answer("⏳ Rasm yangilanmoqda...")

    resp = await update_face_photo(device, passport, str(photo_path))
    if resp.get("status") == "success":
        await message.answer("✅ Rasm muvaffaqiyatli yangilandi!")
    else:
        await message.answer("⚠️ Xatolik: " + resp.get("msg", "unknown"))
    await state.clear()
