from aiogram import Router, types, F
from aiogram.filters import Command
from utils.faceapi import get_users_stats
from bot.keyboards.admin_keyboards import admin_main_keyboard

router = Router()

@router.callback_query(F.data == "users_stats")
async def users_stats(callback: types.CallbackQuery):
    await callback.message.edit_text("⏳ Ma’lumotlar olinmoqda...")
    stats = await get_users_stats()

    if stats["status"] != "ok":
        return await callback.message.edit_text("❌ Statistika olishda xato!", reply_markup=admin_main_keyboard())

    text = (
        "📊 <b>Foydalanuvchilar statistikasi</b>\n\n"
        f"👥 Jami foydalanuvchilar: <b>{stats['total']}</b>\n"
        f"🗓️ Bugun qo‘shilganlar: <b>{stats['today']}</b>\n"
        f"🔁 Duplicate foydalanuvchilar: <b>{stats['duplicates']}</b>"
    )

    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=admin_main_keyboard())
