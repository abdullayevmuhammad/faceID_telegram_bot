# src/bot/handlers/check_user.py
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from utils.storage import user_storage

router = Router()


@router.message(Command("profile"))
@router.message(F.text == "👤 Mening profilim")
async def show_profile(message: Message):
    """Show user profile"""
    user = user_storage.get_user_by_telegram_id(message.from_user.id)

    if not user:
        await message.answer(
            "❌ Siz hali ro'yxatdan o'tmagansiz!\n\n"
            "Ro'yxatdan o'tish uchun /register buyrug'idan foydalaning."
        )
        return

    # Send user data
    text = (
        "👤 <b>Sizning profilingiz:</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"<b>Ism:</b> {user['full_name']}\n"
        f"<b>Telegram ID:</b> <code>{user['telegram_id']}</code>\n"
        f"<b>Pasport:</b> <code>{user['passport']}</code>\n"
        f"<b>Status:</b> {'✅ Faol' if user['is_active'] else '❌ Nofaol'}\n"
        f"<b>Ro'yxatdan o'tgan:</b> {user['created_at'].strftime('%d.%m.%Y %H:%M')}\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "💡 Ma'lumotlarni yangilash uchun: /update"
    )

    await message.answer(text)

    # Send user photo if exists
    if user.get('photo_id'):
        try:
            await message.answer_photo(
                photo=user['photo_id'],
                caption="📸 Sizning rasmingiz"
            )
        except Exception:
            await message.answer("⚠️ Rasmni yuklashda xatolik")


@router.message(F.text == "📝 Ro'yxatdan o'tish")
async def register_button(message: Message):
    """Handle register button"""
    if user_storage.user_exists(message.from_user.id):
        await message.answer(
            "✅ Siz allaqachon ro'yxatdan o'tgansiz!\n\n"
            "Profilingizni ko'rish uchun: /profile\n"
            "Ma'lumotlarni yangilash uchun: /update"
        )
    else:
        await message.answer(
            "📝 Ro'yxatdan o'tish uchun /register buyrug'idan foydalaning."
        )


@router.message(F.text == "ℹ️ Yordam")
@router.message(Command("help"))
async def help_command(message: Message):
    """Show help message"""
    text = (
        "ℹ️ <b>Yordam - Mavjud buyruqlar:</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "<b>👤 Foydalanuvchi buyruqlari:</b>\n"
        "/start - Botni ishga tushirish\n"
        "/register - Ro'yxatdan o'tish\n"
        "/profile - Profilni ko'rish\n"
        "/update - Ma'lumotlarni yangilash\n"
        "/help - Yordam\n\n"
        "<b>👨‍💼 Admin buyruqlari:</b>\n"
        "/admin - Admin panel\n"
        "/users_list - Barcha foydalanuvchilar\n"
        "/user_info [id] - Foydalanuvchi ma'lumoti\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "💡 Tugmalar orqali ham foydalanishingiz mumkin!"
    )

    await message.answer(text)