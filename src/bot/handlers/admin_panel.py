# src/bot/handlers/admin_panel.py
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from utils.db import is_admin, get_admins, promote_to_admin, demote_admin
from utils.faceapi import (
    get_users_stats,
    find_user_in_all_devices,
    send_to_faceid,
    update_face_photo_all,
    delete_from_faceid_all
)
from bot.keyboards.admin_keyboards import admin_main_keyboard
from bot.keyboards.main_menu import admin_main_menu

from pathlib import Path

router = Router()
PHOTO_DIR = Path("tmp_photos")
PHOTO_DIR.mkdir(exist_ok=True)

# =====================================================
# 🧩 State-lar (FSM)
# =====================================================
class AdminManage(StatesGroup):
    add_user_wait_passport = State()
    add_user_wait_photo = State()

    edit_user_wait_passport = State()
    edit_user_wait_photo = State()

    delete_user_wait_passport = State()

    adding_admin_wait_id = State()
    removing_admin_wait_id = State()


# =====================================================
# 📊 Admin panel
# =====================================================
@router.message(Command("admin"))
@router.message(F.text == "📊 Admin panel")
async def show_admin_panel(message: Message):
    if not is_admin(message.from_user.id):
        return await message.answer("❌ Sizda bu bo‘limga kirish huquqi yo‘q.")
    await message.answer("📊 Admin panelga xush kelibsiz:", reply_markup=admin_main_keyboard())


# =====================================================
# 👑 Adminlar ro‘yxati
# =====================================================
@router.callback_query(F.data == "admin_list")
async def cb_admin_list(cq: CallbackQuery):
    if not is_admin(cq.from_user.id):
        return await cq.answer("⛔ Siz admin emassiz", show_alert=True)

    admins = get_admins()
    if not admins:
        await cq.message.edit_text("👑 Adminlar ro‘yxati bo‘sh.", reply_markup=admin_main_keyboard())
        return await cq.answer()

    text = "<b>👑 Adminlar ro‘yxati:</b>\n\n"
    for adm in admins:
        text += f"🆔 <code>{adm['telegram_id']}</code>\n"
        text += f"👤 {adm.get('full_name') or '-'}\n"

    await cq.message.edit_text(text, parse_mode="HTML", reply_markup=admin_main_keyboard())
    await cq.answer()


# =====================================================
# 📈 Statistika
# =====================================================
@router.callback_query(F.data == "users_stats")
async def cb_users_stats(cq: CallbackQuery):
    if not is_admin(cq.from_user.id):
        return await cq.answer("⛔ Siz admin emassiz", show_alert=True)
    await cq.answer()
    stats = await get_users_stats()

    devices = stats.get("devices", [])
    total_all = stats.get("summary", {}).get("total_all", 0)
    today_all = stats.get("summary", {}).get("today_all", 0)

    lines = ["📊 Foydalanuvchilar statistikasi\n"]
    for d in devices:
        lines.append(f"✅ {d.get('host')}\n ├ Jami: {d.get('total')}\n └ Bugun: {d.get('today')}\n")
    lines.append("━━━━━━━━━━━━━━━")
    lines.append(f"📦 Jami foydalanuvchilar: {total_all}")
    lines.append(f"🗓️ Bugun qo‘shilganlar: {today_all}")

    new_text = "\n".join(lines)
    if cq.message.text != new_text:
        await cq.message.edit_text(new_text, parse_mode="HTML", reply_markup=admin_main_keyboard())
    else:
        await cq.answer("🔁 Statistika yangilandi (o‘zgarish yo‘q).", show_alert=False)


# =====================================================
# ➕ Yangi foydalanuvchi qo‘shish (pasport orqali)
# =====================================================
@router.callback_query(F.data == "add_user")
async def cb_add_user(cq: CallbackQuery, state: FSMContext):
    if not is_admin(cq.from_user.id):
        return await cq.answer("⛔ Siz admin emassiz", show_alert=True)
    await cq.message.answer("🪪 Yangi foydalanuvchining pasport raqamini kiriting:")
    await state.set_state(AdminManage.add_user_wait_passport)
    await cq.answer()


@router.message(AdminManage.add_user_wait_passport, F.text)
async def admin_add_user_passport(message: Message, state: FSMContext):
    passport = message.text.strip().upper()
    if not passport or len(passport) < 5:
        return await message.answer("❌ Noto‘g‘ri pasport formati.")

    res = await find_user_in_all_devices(passport)
    if res["status"] == "found":
        await message.answer(f"⚠️ {passport} allaqachon tizimda mavjud.")
        return await state.clear()

    await state.update_data(passport=passport)
    await message.answer(f"📸 Iltimos, {passport} uchun rasm yuboring.")
    await state.set_state(AdminManage.add_user_wait_photo)


@router.message(AdminManage.add_user_wait_photo, F.photo)
async def admin_add_user_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    passport = data.get("passport")

    file = await message.bot.get_file(message.photo[-1].file_id)
    photo_path = PHOTO_DIR / f"{passport}_{message.from_user.id}.jpg"
    await message.bot.download_file(file.file_path, destination=str(photo_path))

    resp = await send_to_faceid(passport, str(photo_path))
    if resp.get("status") == "success":
        await message.answer(f"✅ {passport} foydalanuvchi muvaffaqiyatli qo‘shildi barcha qurilmalarga.")
    else:
        await message.answer(f"⚠️ Xatolik: {resp.get('msg', 'Aniqlanmagan xato')}")

    try:
        photo_path.unlink()
    except Exception:
        pass
    await state.clear()


# =====================================================
# ✏️ Foydalanuvchini tahrirlash
# =====================================================
@router.callback_query(F.data == "edit_user")
async def cb_edit_user(cq: CallbackQuery, state: FSMContext):
    if not is_admin(cq.from_user.id):
        return await cq.answer("⛔ Siz admin emassiz", show_alert=True)
    await cq.message.answer("✏️ O‘zgartiriladigan foydalanuvchi pasport raqamini kiriting:")
    await state.set_state(AdminManage.edit_user_wait_passport)
    await cq.answer()


@router.message(AdminManage.edit_user_wait_passport, F.text)
async def admin_edit_user_passport(message: Message, state: FSMContext):
    passport = message.text.strip().upper()
    res = await find_user_in_all_devices(passport)
    if res["status"] != "found":
        await message.answer(f"❌ {passport} tizimda topilmadi.")
        return await state.clear()

    await state.update_data(passport=passport)
    await message.answer(f"📸 {passport} uchun yangi rasm yuboring:")
    await state.set_state(AdminManage.edit_user_wait_photo)


@router.message(AdminManage.edit_user_wait_photo, F.photo)
async def admin_edit_user_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    passport = data.get("passport")

    file = await message.bot.get_file(message.photo[-1].file_id)
    photo_path = PHOTO_DIR / f"{passport}_{message.from_user.id}.jpg"
    await message.bot.download_file(file.file_path, destination=str(photo_path))

    resp = await update_face_photo_all(passport, str(photo_path))
    if resp.get("status") == "success":
        await message.answer(f"✅ {passport} foydalanuvchi rasmi yangilandi.")
    else:
        await message.answer(f"⚠️ Xatolik: {resp.get('msg', 'Aniqlanmagan xato')}")

    try:
        photo_path.unlink()
    except Exception:
        pass
    await state.clear()


# =====================================================
# 🗑️ Foydalanuvchini o‘chirish
# =====================================================
@router.callback_query(F.data == "delete_user")
async def cb_delete_user(cq: CallbackQuery, state: FSMContext):
    if not is_admin(cq.from_user.id):
        return await cq.answer("⛔ Siz admin emassiz", show_alert=True)
    await cq.message.answer("🗑️ O‘chiriladigan foydalanuvchi pasport raqamini kiriting:")
    await state.set_state(AdminManage.delete_user_wait_passport)
    await cq.answer()


@router.message(AdminManage.delete_user_wait_passport, F.text)
async def admin_delete_user(message: Message, state: FSMContext):
    passport = message.text.strip().upper()
    res = await delete_from_faceid_all(passport)
    if res["status"] == "success":
        success = len([r for r in res["details"] if r["status"] == "success"])
        await message.answer(f"🗑️ {passport} foydalanuvchi {success} qurilmadan muvaffaqiyatli o‘chirildi.")
    else:
        await message.answer(f"⚠️ O‘chirishda xatolik: {res.get('msg', 'Aniqlanmagan xato')}")
    await state.clear()


# =====================================================
# 👑 Admin qo‘shish / o‘chirish
# =====================================================
@router.callback_query(F.data == "add_admin")
async def cb_add_admin(cq: CallbackQuery, state: FSMContext):
    if not is_admin(cq.from_user.id):
        return await cq.answer("⛔ Siz admin emassiz", show_alert=True)
    await cq.message.answer("👑 Yangi adminning Telegram ID sini kiriting:")
    await state.set_state(AdminManage.adding_admin_wait_id)
    await cq.answer()


@router.message(AdminManage.adding_admin_wait_id, F.text)
async def process_adding_admin(message: Message, state: FSMContext):
    try:
        tid = int(message.text.strip())
    except ValueError:
        return await message.answer("❌ Noto‘g‘ri format! Faqat butun son kiriting.")
    promote_to_admin(tid)
    await message.answer(f"✅ <code>{tid}</code> admin sifatida qo‘shildi.", parse_mode="HTML")
    await state.clear()


@router.callback_query(F.data == "remove_admin")
async def cb_remove_admin(cq: CallbackQuery, state: FSMContext):
    if not is_admin(cq.from_user.id):
        return await cq.answer("⛔ Siz admin emassiz", show_alert=True)
    await cq.message.answer("🧹 O‘chiriladigan adminning Telegram ID sini kiriting:")
    await state.set_state(AdminManage.removing_admin_wait_id)
    await cq.answer()


@router.message(AdminManage.removing_admin_wait_id, F.text)
async def process_removing_admin(message: Message, state: FSMContext):
    try:
        tid = int(message.text.strip())
    except ValueError:
        return await message.answer("❌ Noto‘g‘ri format! Faqat butun son kiriting.")
    ok = demote_admin(tid)
    if ok:
        await message.answer(f"🗑️ <code>{tid}</code> admin o‘chirildi.", parse_mode="HTML")
    else:
        await message.answer(f"❌ <code>{tid}</code> topilmadi.", parse_mode="HTML")
    await state.clear()


# =====================================================
# 🔚 Chiqish
# =====================================================
@router.callback_query(F.data == "admin_exit")
async def cb_admin_exit(cq: CallbackQuery):
    if is_admin(cq.from_user.id):
        await cq.message.edit_text("🔙 Admin paneldan chiqildi.")
        await cq.message.answer("Admin panelga qaytish uchun:", reply_markup=admin_main_menu())
    else:
        await cq.answer("⛔ Siz admin emassiz", show_alert=True)
