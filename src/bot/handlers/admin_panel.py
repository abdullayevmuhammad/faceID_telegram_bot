from aiogram import Router, types, F
from aiogram.filters import Command
from utils.faceapi import get_users_stats
from utils.db import get_admins, promote_to_admin, get_user_by_id
from bot.keyboards.admin_keyboards import admin_main_keyboard
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

router = Router()

# FSM holatlari
class AddAdminState(StatesGroup):
    waiting_for_id = State()


@router.message(Command("admin"))
async def admin_panel(message: types.Message):
    """Admin panelni ochish"""
    user = get_user_by_id(message.from_user.id)
    if not user or user["role"] != "admin":
        return await message.answer("🚫 Sizda admin panelga kirish huquqi yo‘q.")

    text = "👨‍💼 <b>Admin panel</b>\n\nQuyidagi bo‘limlardan birini tanlang 👇"
    await message.answer(text, reply_markup=admin_main_keyboard())


# 📊 Foydalanuvchilar statistikasi
from utils.faceapi import get_users_stats

@router.callback_query(F.data == "users_stats")
async def users_stats(callback: types.CallbackQuery):
    await callback.message.edit_text("⏳ Qurilmalardan ma’lumotlar olinmoqda...")

    stats = await get_users_stats()
    if stats["status"] != "ok":
        return await callback.message.edit_text("❌ Statistika olishda xato yuz berdi!", reply_markup=admin_main_keyboard())

    text = "📊 <b>Foydalanuvchilar statistikasi</b>\n\n"

    total_sum = 0
    today_sum = 0

    for d in stats["devices"]:
        status_emoji = "✅" if d["status"] == "ok" else "⚠️"
        text += (
            f"{status_emoji} <b>{d['host'].split('//')[1]}</b>\n"
            f" ├ Jami: <b>{d['total']}</b>\n"
            f" └ Bugun: <b>{d['today']}</b>\n\n"
        )
        total_sum += d["total"]
        today_sum += d["today"]

    text += (
        "━━━━━━━━━━━━━━━\n"
        f"📦 <b>Jami foydalanuvchilar:</b> {total_sum}\n"
        f"🗓️ <b>Bugun qo‘shilganlar:</b> {today_sum}\n"
    )

    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=admin_main_keyboard())


# 👑 Adminlar ro‘yxati
@router.callback_query(F.data == "admin_list")
async def show_admins(callback: types.CallbackQuery):
    admins = get_admins()
    if not admins:
        return await callback.message.edit_text("👑 Hozircha hech qanday admin yo‘q.", reply_markup=admin_main_keyboard())

    text = "👑 <b>Adminlar ro‘yxati:</b>\n\n"
    for adm in admins:
        text += f"🆔 <code>{adm['telegram_id']}</code> — {adm['full_name']}\n📅 {adm['created_at'][:19]}\n\n"

    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=admin_main_keyboard())


# ➕ Yangi admin qo‘shish
@router.callback_query(F.data == "add_admin")
async def add_admin(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "🆕 Yangi admin qo‘shish uchun foydalanuvchining Telegram ID sini yuboring:\n"
        "(ID ni olish uchun foydalanuvchidan /start bosishini so‘rashingiz mumkin.)",
        reply_markup=admin_main_keyboard()
    )
    await state.set_state(AddAdminState.waiting_for_id)


@router.message(AddAdminState.waiting_for_id, F.text.regexp(r"^\d+$"))
async def handle_add_admin(message: types.Message, state: FSMContext):
    tg_id = int(message.text.strip())
    promote_to_admin(tg_id)
    await message.answer(f"✅ Foydalanuvchi <code>{tg_id}</code> admin sifatida belgilandi.", reply_markup=admin_main_keyboard())
    await state.clear()


# 🔙 Chiqish
@router.callback_query(F.data == "admin_exit")
async def admin_exit(callback: types.CallbackQuery):
    await callback.message.edit_text("⬅️ Admin panel yopildi.")

from utils.db import get_admins, demote_admin
from aiogram.fsm.state import State, StatesGroup

class RemoveAdminState(StatesGroup):
    waiting_for_id = State()


# 🗑 Adminni olib tashlashni tanlash
@router.callback_query(F.data == "remove_admin")
async def start_remove_admin(callback: types.CallbackQuery, state: FSMContext):
    admins = get_admins()
    if not admins:
        return await callback.message.edit_text("👑 Hech qanday admin topilmadi.", reply_markup=admin_main_keyboard())

    text = "🗑 <b>Adminni olib tashlash</b>\n\n"
    text += "Quyidagi adminlardan birining <code>Telegram ID</code> sini kiriting:\n\n"
    for adm in admins:
        text += f"🆔 <code>{adm['telegram_id']}</code> — {adm['full_name']}\n📅 {adm['created_at'][:19]}\n\n"

    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=admin_main_keyboard())
    await state.set_state(RemoveAdminState.waiting_for_id)


# 🧾 Admin ID qabul qilish
@router.message(RemoveAdminState.waiting_for_id, F.text.regexp(r"^\d+$"))
async def handle_remove_admin(message: types.Message, state: FSMContext):
    tg_id = int(message.text.strip())

    if tg_id == message.from_user.id:
        return await message.answer("⚠️ O‘zingizni admin ro‘yxatidan o‘chira olmaysiz.", reply_markup=admin_main_keyboard())

    demote_admin(tg_id)
    await message.answer(f"✅ <code>{tg_id}</code> endi oddiy foydalanuvchi bo‘ldi.", reply_markup=admin_main_keyboard())
    await state.clear()

