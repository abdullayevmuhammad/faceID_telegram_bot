# src/bot/handlers/menu_actions.py
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from bot.handlers import register_user, profile, update_photo, admin_panel
from bot.config import ADMIN_ID

router = Router()

# 🔹 Tugma: Ro‘yxatdan o‘tish
@router.message(F.text.in_(["🪪 Ro'yxatdan o'tish", "📝 Ro'yxatdan o'tish"]))
async def button_register(message: Message, state: FSMContext):
    await register_user.start_register(message, state)


# 🔹 Tugma: Profilim
@router.message(F.text.in_(["👤 Profilim", "👤 Mening profilim"]))
async def button_profile(message: Message):
    await profile.profile_cmd(message)


# 🔹 Tugma: Ma’lumotni yangilash
@router.message(F.text == "🔄 Ma'lumotni yangilash")
async def button_update(message: Message, state: FSMContext):
    # FSM contextni to‘g‘ridan-to‘g‘ri uzatamiz
    await update_photo.start_update(message, state)


# 🔹 Tugma: Admin panel
@router.message(F.text == "📊 Admin panel")
async def button_admin(message: Message):
    print("Admin ID:", ADMIN_ID)
    print("Foydalanuvchi ID:", message.from_user.id)
    if message.from_user.id != ADMIN_ID:
        await message.answer("🚫 Sizda admin panelga kirish huquqi yo'q.")
        return

    await admin_panel.admin_panel(message)


# 🔹 Tugma: Yordam
@router.message(F.text == "ℹ️ Yordam")
async def button_help(message: Message):
    await message.answer(
        "ℹ️ <b>Yordam:</b>\n\n"
        "🪪 Ro‘yxatdan o‘tish — pasport va rasm yuborish orqali tizimga kirish.\n"
        "👤 Profilim — o‘zingiz haqidagi ma’lumotni ko‘rish.\n"
        "🔄 Ma’lumotni yangilash — pasport yoki rasmni yangilash.\n"
        "📊 Admin panel — faqat administrator uchun.\n\n"
        "Savollar bo‘lsa: @admin bilan bog‘laning."
    )
