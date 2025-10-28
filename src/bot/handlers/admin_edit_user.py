# src/bot/handlers/admin_edit_user.py
from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from src.bot.states.admin_states import AdminManage
from utils.faceapi import find_user_in_all_devices, update_face_photo_all, send_to_faceid, copy_user_to_missing_devices
from utils.db import add_user, get_user_by_passport

from pathlib import Path
PHOTO_DIR = Path("tmp_photos")
PHOTO_DIR.mkdir(exist_ok=True)

router = Router()

@router.message(AdminManage.adding_admin_wait_id)
async def process_adding_admin(message: Message, state: FSMContext):
    try:
        tid = int(message.text.strip())
    except Exception:
        return await message.answer("❌ Noto'g'ri format! Iltimos, butun sonli Telegram ID yuboring.")
    # add_admin function in db will be used from admin_panel handler after confirm? We call db here.
    from utils.db import add_admin
    add_admin(telegram_id=tid, username=message.from_user.username or "", full_name="")
    await message.answer(f"✅ <code>{tid}</code> admin sifatida qo'shildi.", parse_mode="HTML")
    await state.clear()

@router.message(AdminManage.removing_admin_wait_id)
async def process_removing_admin(message: Message, state: FSMContext):
    try:
        tid = int(message.text.strip())
    except Exception:
        return await message.answer("❌ Noto'g'ri format! Iltimos, butun sonli Telegram ID yuboring.")
    from utils.db import remove_admin
    ok = remove_admin(tid)
    if ok:
        await message.answer(f"🗑️ <code>{tid}</code> admin sifatida olib tashlandi.", parse_mode="HTML")
    else:
        await message.answer(f"❌ <code>{tid}</code> topilmadi.", parse_mode="HTML")
    await state.clear()

# Admin: edit user passport
@router.message(AdminManage.edit_user_wait_passport)
async def admin_edit_user_passport(message: Message, state: FSMContext):
    passport = message.text.strip().upper()
    # simple format check
    if not passport or len(passport) < 5:
        return await message.answer("❌ Noto'g'ri pasport formati.")
    # find via faceapi
    res = await find_user_in_all_devices(passport)
    if res["status"] == "found":
        await message.answer(f"🔎 {passport} topildi.\n📸 Iltimos, yangi rasm yuboring (photo).")
        await state.update_data(passport=passport, found_devices=res["devices"])
        await state.set_state(AdminManage.edit_user_wait_photo)
    else:
        await message.answer(f"⚠️ {passport} tizimda topilmadi.")
        await state.clear()

@router.message(AdminManage.edit_user_wait_photo, content_types=["photo"])
async def admin_edit_user_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    passport = data.get("passport")
    if not passport:
        await message.answer("❌ Ichki xato. Iltimos, qaytadan boshlang.")
        await state.clear()
        return

    file = await message.bot.get_file(message.photo[-1].file_id)
    photo_path = PHOTO_DIR / f"{passport}_{message.from_user.id}.jpg"
    await message.bot.download_file(file.file_path, destination=str(photo_path))

    resp = await update_face_photo_all(passport, str(photo_path))
    if resp.get("status") == "success":
        await message.answer(f"✅ {passport} ning rasmı yangilandi.", parse_mode="HTML")
    else:
        await message.answer(f"⚠️ Xatolik: {resp.get('msg', 'unknown')}")
    try:
        photo_path.unlink()
    except Exception:
        pass
    await state.clear()

# Admin: add user flow (admin forces add)
@router.message(AdminManage.add_user_wait_passport)
async def admin_add_user_passport(message: Message, state: FSMContext):
    passport = message.text.strip().upper()
    if not passport:
        return await message.answer("❌ Noto'g'ri pasport.")
    # If already exists on any device, ask whether to copy or update; for simplicity ask photo now
    await state.update_data(passport=passport)
    await message.answer("📸 Iltimos, rasm yuboring:")
    await state.set_state(AdminManage.add_user_wait_photo)

@router.message(AdminManage.add_user_wait_photo, content_types=["photo"])
async def admin_add_user_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    passport = data.get("passport")
    file = await message.bot.get_file(message.photo[-1].file_id)
    photo_path = PHOTO_DIR / f"{passport}_{message.from_user.id}.jpg"
    await message.bot.download_file(file.file_path, destination=str(photo_path))

    resp = await send_to_faceid(passport, str(photo_path))
    if resp.get("status") == "success":
        await message.answer(f"✅ {passport} muvaffaqiyatli qo'shildi barcha qurilmalarga.")
    else:
        await message.answer(f"⚠️ Xatolik: {resp.get('msg', 'unknown')}")
    try:
        photo_path.unlink()
    except Exception:
        pass
    await state.clear()
