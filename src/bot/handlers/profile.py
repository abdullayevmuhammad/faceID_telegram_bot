from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from utils.storage import user_storage

router = Router()

@router.message(Command("profile"))
async def profile_cmd(message: Message):
    user = user_storage.get_user_by_telegram_id(message.from_user.id)
    if not user:
        return await message.answer("❌ Siz hali ro‘yxatdan o‘tmagansiz.\n/register ni yuboring.")

    text = (
        f"👤 <b>Profilingiz:</b>\n"
        f"👥 Ism: {user['full_name']}\n"
        f"🪪 Pasport: {user['passport']}\n"
        f"📅 Ro‘yxatdan o‘tgan: {user['created_at'].strftime('%d.%m.%Y %H:%M')}\n"
    )
    await message.answer(text)

    if user.get("photo_id"):
        await message.answer_photo(user["photo_id"], caption="📸 Sizning rasmingiz")
