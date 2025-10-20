from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from utils.storage_db import user_storage_db

router = Router()

@router.message(Command("profile"))
async def user_profile(message: Message):
    user = await user_storage_db.get_user_by_telegram_id(message.from_user.id)

    if not user:
        await message.answer("❌ Siz hali ro'yxatdan o'tmagansiz. /register buyrug'idan foydalaning.")
        return

    text = (
        f"👤 <b>Profilingiz:</b>\n\n"
        f"👥 Ism: <b>{user.get('full_name','—')}</b>\n"
        f"🪪 Pasport: <code>{user.get('passport','—')}</code>\n"
        f"🆔 Telegram ID: <code>{user.get('telegram_id')}</code>\n"
        f"📅 Ro‘yxatdan o‘tgan: {user.get('created_at').strftime('%d.%m.%Y %H:%M') if user.get('created_at') else '—'}\n"
        f"🔄 FaceID status: {user.get('faceid_status','—')}\n"
    )

    await message.answer(text)
