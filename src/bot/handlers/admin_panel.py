# src/bot/handlers/admin_panel.py
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from bot.config import ADMIN_ID
from utils.storage import user_storage

router = Router()


def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    return user_id == ADMIN_ID


@router.message(Command("admin"))
async def admin_panel(message: Message):
    """Admin statistics panel"""
    if not is_admin(message.from_user.id):
        await message.answer("🚫 Sizda bu buyruqdan foydalanish huquqi yo'q.")
        return

    # Get statistics
    total_users = user_storage.get_total_users()
    today_users = user_storage.get_today_users()
    duplicates = len(user_storage.find_duplicate_passports())

    text = (
        "📊 <b>Face ID Tizimi Statistikasi</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👥 Jami foydalanuvchilar: <b>{total_users}</b>\n"
        f"🗓️ Bugun qo'shilganlar: <b>{today_users}</b>\n"
        f"🔁 Duplicate foydalanuvchilar: <b>{duplicates}</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "💡 <i>Qo'shimcha buyruqlar:</i>\n"
        "/users_list - Barcha foydalanuvchilar\n"
        "/user_info [telegram_id] - Foydalanuvchi ma'lumoti"
    )

    await message.answer(text)


@router.message(Command("users_list"))
async def list_users(message: Message):
    """List all registered users"""
    if not is_admin(message.from_user.id):
        await message.answer("🚫 Sizda bu buyruqdan foydalanish huquqi yo'q.")
        return

    users = user_storage.get_all_users()

    if not users:
        await message.answer("📭 Hozircha ro'yxatdan o'tgan foydalanuvchilar yo'q.")
        return

    text = "👥 <b>Ro'yxatdan o'tgan foydalanuvchilar:</b>\n\n"

    for i, user in enumerate(users, 1):
        text += (
            f"{i}. <b>{user['full_name']}</b>\n"
            f"   🪪 {user['passport']}\n"
            f"   🆔 {user['telegram_id']}\n"
            f"   📅 {user['created_at'].strftime('%d.%m.%Y %H:%M')}\n\n"
        )

    # Split message if too long
    if len(text) > 4000:
        parts = [text[i:i + 4000] for i in range(0, len(text), 4000)]
        for part in parts:
            await message.answer(part)
    else:
        await message.answer(text)


@router.message(Command("user_info"))
async def user_info(message: Message):
    """Get specific user info"""
    if not is_admin(message.from_user.id):
        await message.answer("🚫 Sizda bu buyruqdan foydalanish huquqi yo'q.")
        return

    # Extract telegram_id from command
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

    user = user_storage.get_user_by_telegram_id(telegram_id)

    if not user:
        await message.answer(f"❌ Telegram ID <code>{telegram_id}</code> topilmadi.")
        return

    text = (
        "👤 <b>Foydalanuvchi ma'lumotlari:</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"<b>Ism:</b> {user['full_name']}\n"
        f"<b>Telegram ID:</b> <code>{user['telegram_id']}</code>\n"
        f"<b>Pasport:</b> <code>{user['passport']}</code>\n"
        f"<b>Rasm ID:</b> <code>{user['photo_id']}</code>\n"
        f"<b>Rol:</b> {user['role']}\n"
        f"<b>Status:</b> {'✅ Faol' if user['is_active'] else '❌ Nofaol'}\n"
        f"<b>Ro'yxatdan o'tgan:</b> {user['created_at'].strftime('%d.%m.%Y %H:%M')}\n"
        f"<b>Yangilangan:</b> {user['updated_at'].strftime('%d.%m.%Y %H:%M')}\n"
    )

    await message.answer(text)