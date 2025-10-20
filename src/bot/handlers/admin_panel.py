# src/bot/handlers/admin_panel.py
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from bot.config import ADMIN_ID
from utils.storage_db import user_storage_db  # async DB-backed storage

router = Router()


def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    return user_id == ADMIN_ID


@router.message(Command("admin"))
async def admin_panel(message: Message):
    """Admin statistics panel (async DB)"""
    if not is_admin(message.from_user.id):
        await message.answer("🚫 Sizda bu buyruqdan foydalanish huquqi yo'q.")
        return

    # Get statistics from database
    total_users = await user_storage_db.get_total_users()
    today_users = await user_storage_db.get_today_users()
    duplicates = await user_storage_db.find_duplicate_passports()

    text = (
        "📊 <b>Face ID Tizimi Statistikasi</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👥 Jami foydalanuvchilar: <b>{total_users}</b>\n"
        f"🗓️ Bugun qo'shilganlar: <b>{today_users}</b>\n"
        f"🔁 Duplicate foydalanuvchilar: <b>{len(duplicates)}</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "💡 <i>Qo'shimcha buyruqlar:</i>\n"
        "/users_list - Barcha foydalanuvchilar\n"
        "/user_info [telegram_id] - Foydalanuvchi ma'lumoti"
    )

    await message.answer(text)


@router.message(Command("users_list"))
async def list_users(message: Message):
    """List all registered users (DB)"""
    if not is_admin(message.from_user.id):
        await message.answer("🚫 Sizda bu buyruqdan foydalanish huquqi yo'q.")
        return

    users = await user_storage_db.get_all_users()

    if not users:
        await message.answer("📭 Hozircha ro'yxatdan o'tgan foydalanuvchilar yo'q.")
        return

    parts = []
    header = "👥 <b>Ro'yxatdan o'tgan foydalanuvchilar:</b>\n\n"
    current = header

    for i, user in enumerate(users, 1):
        created = user.get("created_at")
        created_str = created.strftime('%d.%m.%Y %H:%M') if created else "—"
        current += (
            f"{i}. <b>{user.get('full_name','—')}</b>\n"
            f"   🪪 {user.get('passport','—')}\n"
            f"   🆔 {user.get('telegram_id','—')}\n"
            f"   📅 {created_str}\n\n"
        )
        # split if current too long
        if len(current) > 3500:
            parts.append(current)
            current = ""

    if current:
        parts.append(current)

    for part in parts:
        await message.answer(part)


@router.message(Command("user_info"))
async def user_info(message: Message):
    """Get specific user info (DB)"""
    if not is_admin(message.from_user.id):
        await message.answer("🚫 Sizda bu buyruqdan foydalanish huquqi yo'q.")
        return

    parts = message.text.split()
    if len(parts) < 2:
        await message.answer(
            "❌ Noto'g'ri format!\n\n"
            "To'g'ri format: <code>/user_info [telegram_id]</code>\n"
            "Masalan: <code>/user_info 123456789</code>"
        )
        return

    try:
        telegram_id = int(parts[1])
    except ValueError:
        await message.answer("❌ Telegram ID raqam bo'lishi kerak!")
        return

    user = await user_storage_db.get_user_by_telegram_id(telegram_id)

    if not user:
        await message.answer(f"❌ Telegram ID <code>{telegram_id}</code> topilmadi.")
        return

    # Normalize fields safely
    full_name = user.get("full_name", "—")
    telegram_id = user.get("telegram_id", "—")
    passport = user.get("passport", "—")
    photo_id = user.get("photo_id", "—")
    role = user.get("role", "user")
    is_active = user.get("is_active", True)
    created_at = user.get("created_at")
    updated_at = user.get("updated_at")

    created_str = created_at.strftime('%d.%m.%Y %H:%M') if created_at else "—"
    updated_str = updated_at.strftime('%d.%m.%Y %H:%M') if updated_at else "—"

    text = (
        "👤 <b>Foydalanuvchi ma'lumotlari:</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"<b>Ism:</b> {full_name}\n"
        f"<b>Telegram ID:</b> <code>{telegram_id}</code>\n"
        f"<b>Pasport:</b> <code>{passport}</code>\n"
        f"<b>Rasm ID:</b> <code>{photo_id}</code>\n"
        f"<b>Rol:</b> {role}\n"
        f"<b>Status:</b> {'✅ Faol' if is_active else '❌ Nofaol'}\n"
        f"<b>Ro'yxatdan o'tgan:</b> {created_str}\n"
        f"<b>Yangilangan:</b> {updated_str}\n"
    )

    await message.answer(text)
