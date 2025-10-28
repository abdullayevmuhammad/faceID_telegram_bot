# src/bot/handlers/admin_edit_user.py
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from pathlib import Path

from bot.states.admin_states import AdminManage
from utils.faceapi import (
    find_user_in_all_devices,
    update_face_photo_all,
    send_to_faceid,
    delete_from_faceid_all
)
from utils.db import is_admin, promote_to_admin, demote_admin

from utils.faceapi import get_users_stats

from utils.db import get_admins

PHOTO_DIR = Path("tmp_photos")
PHOTO_DIR.mkdir(exist_ok=True)

router = Router()


# ========================
# 👑 ADMIN QO‘SHISH
# ========================
@router.message(AdminManage.adding_admin_wait_id)
async def process_adding_admin(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return await message.answer("⛔ Siz admin emassiz.")
    try:
        tid = int(message.text.strip())
    except ValueError:
        return await message.answer("❌ Noto'g'ri format! Iltimos, butun sonli Telegram ID yuboring.")

    promote_to_admin(telegram_id=tid, username=message.from_user.username or "", full_name="")
    await message.answer(f"✅ <code>{tid}</code> admin sifatida qo‘shildi.", parse_mode="HTML")
    await state.clear()


# ========================
# 🧹 ADMIN O‘CHIRISH
# ========================
@router.message(AdminManage.removing_admin_wait_id, F.text)
async def process_removing_admin(message: Message, state: FSMContext):
    try:
        tid = int(message.text.strip())
    except ValueError:
        return await message.answer("❌ Noto‘g‘ri format! Faqat butun son kiriting.")

    from utils.db import get_user_by_id, demote_admin
    user = get_user_by_id(tid)
    if not user:
        await message.answer(f"❌ <code>{tid}</code> topilmadi.", parse_mode="HTML")
    else:
        demote_admin(tid)
        await message.answer(f"🗑️ <code>{tid}</code> admin o‘chirildi.", parse_mode="HTML")

    await state.clear()



# ========================
# ➕ FOYDALANUVCHI QO‘SHISH
# ========================
@router.message(AdminManage.add_user_wait_passport)
async def admin_add_user_passport(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return await message.answer("⛔ Siz admin emassiz.")
    passport = message.text.strip().upper()

    if not passport or len(passport) < 5:
        return await message.answer("❌ Noto‘g‘ri pasport formati.")

    res = await find_user_in_all_devices(passport)
    if res["status"] == "found":
        return await message.answer(f"⚠️ {passport} allaqachon mavjud tizimda.")
    else:
        await state.update_data(passport=passport)
        await message.answer(f"📸 {passport} uchun rasm yuboring:")
        await state.set_state(AdminManage.add_user_wait_photo)


@router.message(AdminManage.add_user_wait_photo, F.photo)
async def admin_add_user_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    passport = data.get("passport")
    if not passport:
        await message.answer("⚠️ Xatolik. Qaytadan urinib ko‘ring.")
        return await state.clear()

    file = await message.bot.get_file(message.photo[-1].file_id)
    photo_path = PHOTO_DIR / f"{passport}_{message.from_user.id}.jpg"
    await message.bot.download_file(file.file_path, destination=str(photo_path))

    resp = await send_to_faceid(passport, str(photo_path))
    if resp.get("status") == "success":
        await message.answer(f"✅ {passport} foydalanuvchi qo‘shildi barcha qurilmalarga.")
    else:
        await message.answer(f"⚠️ Xatolik: {resp.get('msg', 'Aniqlanmagan xato')}")

    try:
        photo_path.unlink()
    except Exception:
        pass

    await state.clear()


# ========================
# ✏️ FOYDALANUVCHINI TAHRIRLASH
# ========================
@router.message(AdminManage.edit_user_wait_passport)
async def admin_edit_user_passport(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return await message.answer("⛔ Siz admin emassiz.")
    passport = message.text.strip().upper()

    res = await find_user_in_all_devices(passport)
    if res["status"] == "found":
        await message.answer(f"📸 {passport} uchun yangi rasm yuboring:")
        await state.update_data(passport=passport)
        await state.set_state(AdminManage.edit_user_wait_photo)
    else:
        await message.answer(f"❌ {passport} tizimda topilmadi.")
        await state.clear()


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


# ========================
# 🗑️ FOYDALANUVCHINI O‘CHIRISH
# ========================
@router.message(AdminManage.delete_user_wait_passport)
async def admin_delete_user(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return await message.answer("⛔ Siz admin emassiz.")
    passport = message.text.strip().upper()

    res = await delete_from_faceid_all(passport)
    if res["status"] == "success":
        success = len([r for r in res["details"] if r["status"] == "success"])
        await message.answer(f"🗑️ {passport} o‘chirildi ({success} qurilmada muvaffaqiyatli).")
    else:
        await message.answer(f"❌ O‘chirishda xatolik: {res.get('msg', 'Aniqlanmagan xato')}")
    await state.clear()


# =====================================================
# ⚙️ Komandalar orqali admin funksiyalari
# =====================================================
from aiogram.filters import Command

# /admin — admin panelni ochish
@router.message(Command("admin"))
async def cmd_admin(message: Message):
    if not is_admin(message.from_user.id):
        return await message.answer("⛔ Siz admin emassiz.")
    await message.answer("📊 Admin panelga xush kelibsiz:", reply_markup=admin_main_keyboard())


# /admin_list — adminlar ro‘yxatini ko‘rish
@router.message(Command("admin_list"))
async def cmd_admin_list(message: Message):
    if not is_admin(message.from_user.id):
        return await message.answer("⛔ Siz admin emassiz.")
    admins = get_admins()
    if not admins:
        return await message.answer("👑 Adminlar ro‘yxati bo‘sh.")
    text = "<b>👑 Adminlar ro‘yxati:</b>\n\n"
    for adm in admins:
        text += f"🆔 <code>{adm['telegram_id']}</code>\n"
        text += f"👤 {adm.get('full_name') or '-'}\n"
        text += f"@{adm.get('username') or '-'}\n\n"
    await message.answer(text, parse_mode="HTML")


# /add_admin — yangi admin qo‘shish
@router.message(Command("add_admin"))
async def cmd_add_admin(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return await message.answer("⛔ Siz admin emassiz.")
    await message.answer("👑 Yangi adminning Telegram ID sini kiriting:")
    await state.set_state(AdminManage.adding_admin_wait_id)


# /adduser — foydalanuvchi qo‘shish
@router.message(Command("adduser"))
async def cmd_add_user(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return await message.answer("⛔ Siz admin emassiz.")
    await message.answer("🪪 Yangi foydalanuvchining pasport raqamini kiriting:")
    await state.set_state(AdminManage.add_user_wait_passport)


# /update_user — foydalanuvchini tahrirlash
@router.message(Command("update_user"))
async def cmd_update_user(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return await message.answer("⛔ Siz admin emassiz.")
    await message.answer("✏️ O‘zgartiriladigan foydalanuvchi pasport raqamini kiriting:")
    await state.set_state(AdminManage.edit_user_wait_passport)


# /stats — foydalanuvchi statistikasi
@router.message(Command("stats"))
async def cmd_stats(message: Message):
    if not is_admin(message.from_user.id):
        return await message.answer("⛔ Siz admin emassiz.")
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

    await message.answer("\n".join(lines), parse_mode="HTML")



# /remove_admin — adminni o‘chirish
@router.message(Command("remove_admin"))
async def cmd_remove_admin(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return await message.answer("⛔ Siz admin emassiz.")
    await message.answer("🧹 O‘chiriladigan adminning Telegram ID sini kiriting:")
    await state.set_state(AdminManage.removing_admin_wait_id)

@router.message(Command("help"))
async def cmd_help(message: Message):
    if is_admin(message.from_user.id):
        text = (
            "👑 <b>Admin komandalar:</b>\n"
            "/admin — Admin panel\n"
            "/admin_list — Adminlar ro‘yxatini ko‘rish\n"
            "/add_admin — Yangi admin qo‘shish\n"
            "/adduser — Yangi foydalanuvchi qo‘shish\n"
            "/update_user — Foydalanuvchini tahrirlash\n"
            "/stats — Statistika\n"
        )
    else:
        text = (
            "👤 <b>Foydalanuvchi komandalar:</b>\n"
            "/start — Boshlash\n"
            "/register — Ro‘yxatdan o‘tish\n"
            "/profile — Profilni ko‘rish\n"
            "/update — Rasmni yangilash\n"
            "/help — Yordam olish\n"
        )
    await message.answer(text, parse_mode="HTML")
