from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from utils.storage import user_storage

router = Router()

from utils.db import get_user_by_id

@router.message(Command("profile"))
async def profile_cmd(message: Message):
    user = get_user_by_id(message.from_user.id)
    if not user:
        return await message.answer("❌ Siz hali ro‘yxatdan o‘tmagansiz.\n/register ni yuboring.")

    text = (
        f"👤 <b>Profilingiz:</b>\n"
        f"🪪 Pasport: <b>{user['passport']}</b>\n"
        f"👥 Ism: {user['full_name']}\n"
        f"📅 Ro‘yxatdan o‘tgan: {user['created_at'][:19]}\n"
    )
    if user["photo_id"]:
        await message.answer_photo(user["photo_id"], caption=text)
    else:
        await message.answer(text)
