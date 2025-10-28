from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from utils.db import (
    is_admin,
    get_admins,
    get_user_by_id,
    add_user,
    promote_to_admin,
    demote_admin
)
from utils.faceapi import get_users_stats
from bot.keyboards.admin_keyboards import admin_main_keyboard
from bot.keyboards.main_menu import admin_main_menu

router = Router()


# =====================================================
# 🧩 State-lar (FSM)
# =====================================================
class AdminManage(StatesGroup):
    adding_user_wait_id = State()
    adding_user_wait_passport = State()
    adding_user_wait_name = State()
    editing_user_wait_passport = State()
    editing_user_wait_new_name = State()


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
@router.callback_query(lambda c: c.data == "admin_list")
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
        text += f"@{adm.get('username') or '-'}\n\n"

    await cq.message.edit_text(text, parse_mode="HTML", reply_markup=admin_main_keyboard())
    await cq.answer()


# =====================================================
# 📈 Statistika
# =====================================================
@router.callback_query(lambda c: c.data == "users_stats")
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

    await cq.message.edit_text("\n".join(lines), parse_mode="HTML", reply_markup=admin_main_keyboard())


# =====================================================
# ➕ Foydalanuvchi qo‘shish
# =====================================================
@router.callback_query(lambda c: c.data == "add_user")
async def cb_add_user(cq: CallbackQuery, state: FSMContext):
    if not is_admin(cq.from_user.id):
        return await cq.answer("⛔ Siz admin emassiz", show_alert=True)
    await cq.message.answer("➕ Yangi foydalanuvchining Telegram ID sini kiriting:")
    await state.set_state(AdminManage.adding_user_wait_id)
    await cq.answer()


@router.message(AdminManage.adding_user_wait_id)
async def admin_add_user_get_id(message: Message, state: FSMContext):
    try:
        telegram_id = int(message.text.strip())
        await state.update_data(new_user_id=telegram_id)
        await message.answer("🪪 Endi foydalanuvchining passport raqamini kiriting (masalan: AB1234567):")
        await state.set_state(AdminManage.adding_user_wait_passport)
    except ValueError:
        await message.answer("❌ Noto‘g‘ri ID! Iltimos, faqat raqam kiriting.")


@router.message(AdminManage.adding_user_wait_passport)
async def admin_add_user_get_passport(message: Message, state: FSMContext):
    passport = message.text.strip().upper()
    await state.update_data(new_passport=passport)
    await message.answer("👤 Endi foydalanuvchining to‘liq ismini kiriting:")
    await state.set_state(AdminManage.adding_user_wait_name)


@router.message(AdminManage.adding_user_wait_name)
async def admin_add_user_save(message: Message, state: FSMContext):
    data = await state.get_data()
    telegram_id = data["new_user_id"]
    passport = data["new_passport"]
    full_name = message.text.strip()

    add_user(telegram_id, passport=passport, full_name=full_name, role="user")
    await message.answer(f"✅ Foydalanuvchi qo‘shildi:\n🆔 {telegram_id}\n🪪 {passport}\n👤 {full_name}",
                         reply_markup=admin_main_keyboard())
    await state.clear()


# =====================================================
# ✏️ Foydalanuvchini o‘zgartirish
# =====================================================
@router.callback_query(lambda c: c.data == "edit_user")
async def cb_edit_user(cq: CallbackQuery, state: FSMContext):
    if not is_admin(cq.from_user.id):
        return await cq.answer("⛔ Siz admin emassiz", show_alert=True)
    await cq.message.answer("🔎 O‘zgartiriladigan foydalanuvchi pasport raqamini kiriting:")
    await state.set_state(AdminManage.editing_user_wait_passport)
    await cq.answer()


@router.message(AdminManage.editing_user_wait_passport)
async def admin_edit_user_find(message: Message, state: FSMContext):
    passport = message.text.strip().upper()
    conn_user = None

    # foydalanuvchini passport orqali topamiz
    from utils.db import get_conn
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE passport = ?", (passport,))
    row = cur.fetchone()
    conn.close()

    if not row:
        await message.answer("❌ Bunday foydalanuvchi topilmadi.")
        await state.clear()
        return

    conn_user = dict(row)
    await state.update_data(editing_user_id=conn_user["telegram_id"])
    await message.answer(
        f"🧾 Foydalanuvchi topildi:\n"
        f"👤 {conn_user['full_name']}\n"
        f"🪪 {conn_user['passport']}\n\n"
        f"Yangi ismni kiriting:"
    )
    await state.set_state(AdminManage.editing_user_wait_new_name)


@router.message(AdminManage.editing_user_wait_new_name)
async def admin_edit_user_update(message: Message, state: FSMContext):
    data = await state.get_data()
    telegram_id = data.get("editing_user_id")
    new_name = message.text.strip()

    if not telegram_id:
        await message.answer("⚠️ Xatolik: foydalanuvchi aniqlanmadi.")
        await state.clear()
        return

    from utils.db import get_conn
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE users SET full_name = ? WHERE telegram_id = ?", (new_name, telegram_id))
    conn.commit()
    conn.close()

    await message.answer(f"✅ Foydalanuvchi ismi yangilandi: {new_name}", reply_markup=admin_main_keyboard())
    await state.clear()


# =====================================================
# 🔚 Chiqish
# =====================================================
@router.callback_query(lambda c: c.data == "admin_exit")
async def cb_admin_exit(cq: CallbackQuery):
    if is_admin(cq.from_user.id):
        await cq.message.edit_text("🔙 Admin paneldan chiqildi.")
        await cq.message.answer("Admin panelga qaytish uchun:", reply_markup=admin_main_menu())
    else:
        await cq.answer("⛔ Siz admin emassiz", show_alert=True)
