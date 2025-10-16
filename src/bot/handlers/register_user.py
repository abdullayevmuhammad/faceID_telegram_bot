# src/bot/handlers/register_user.py
import re
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from bot.states.register_states import RegisterUser
from utils.storage import user_storage
from bot.keyboards.user_keyboards import cancel_keyboard

router = Router()


@router.message(Command("register"))
async def start_register(message: Message, state: FSMContext):
    """Start registration process"""

    # Check if already registered
    if user_storage.user_exists(message.from_user.id):
        user = user_storage.get_user_by_telegram_id(message.from_user.id)
        await message.answer(
            f"ℹ️ Siz allaqachon ro'yxatdan o'tgansiz!\n\n"
            f"👤 Ism: <b>{user['full_name']}</b>\n"
            f"🪪 Pasport: <b>{user['passport']}</b>\n\n"
            "Ma'lumotlarni yangilash uchun /update buyrug'idan foydalaning."
        )
        return

    await message.answer(
        "📝 <b>Ro'yxatdan o'tish</b>\n\n"
        "🪪 Pasport seriya raqamingizni kiriting:\n"
        "Format: <code>AB1234567</code>\n\n"
        "Masalan: AA1234567, AB9876543",
        reply_markup=cancel_keyboard()
    )
    await state.set_state(RegisterUser.waiting_for_passport)


@router.message(RegisterUser.waiting_for_passport, F.text == "❌ Bekor qilish")
async def cancel_registration(message: Message, state: FSMContext):
    """Cancel registration"""
    await state.clear()
    await message.answer("❌ Ro'yxatdan o'tish bekor qilindi.", reply_markup=None)


@router.message(RegisterUser.waiting_for_passport)
async def process_passport(message: Message, state: FSMContext):
    """Process passport number"""
    passport = message.text.strip().upper()

    # Validate format: 2 letters + 7 digits
    if not re.match(r"^[A-Z]{2}\d{7}$", passport):
        await message.answer(
            "❌ Noto'g'ri format!\n\n"
            "To'g'ri format: <code>AB1234567</code>\n"
            "(2 ta lotin harfi + 7 ta raqam)\n\n"
            "Qaytadan kiriting:"
        )
        return

    # Check if passport already exists
    if user_storage.passport_exists(passport):
        await message.answer(
            "⚠️ Bu pasport raqami allaqachon ro'yxatdan o'tgan!\n\n"
            "Agar bu sizning pasportingiz bo'lsa, admin bilan bog'laning."
        )
        await state.clear()
        return

    await state.update_data(passport=passport)
    await message.answer(
        "✅ Pasport qabul qilindi!\n\n"
        "📸 Endi yuzingizning <b>aniq rasmini</b> yuboring:\n\n"
        "⚠️ <i>Rasm sifatli va yaxshi yoritilgan bo'lishi kerak!</i>",
        reply_markup=cancel_keyboard()
    )
    await state.set_state(RegisterUser.waiting_for_photo)


@router.message(RegisterUser.waiting_for_photo, F.text == "❌ Bekor qilish")
async def cancel_photo(message: Message, state: FSMContext):
    """Cancel photo upload"""
    await state.clear()
    await message.answer("❌ Ro'yxatdan o'tish bekor qilindi.", reply_markup=None)


@router.message(RegisterUser.waiting_for_photo, F.photo)
async def process_photo(message: Message, state: FSMContext):
    """Process user photo and complete registration"""
    user_data = await state.get_data()
    passport = user_data.get("passport")
    photo_id = message.photo[-1].file_id  # Get highest quality photo

    # Save user to storage
    user = user_storage.add_user(
        telegram_id=message.from_user.id,
        full_name=message.from_user.full_name or "Unknown",
        passport=passport,
        photo_id=photo_id
    )

    await message.answer(
        "🎉 <b>Tabriklaymiz!</b>\n\n"
        "✅ Siz muvaffaqiyatli ro'yxatdan o'tdingiz!\n\n"
        f"👤 Ism: <b>{user['full_name']}</b>\n"
        f"🪪 Pasport: <b>{user['passport']}</b>\n"
        f"📅 Sana: <b>{user['created_at'].strftime('%d.%m.%Y %H:%M')}</b>\n\n"
        "✨ Endi siz tizimdan foydalanishingiz mumkin!",
        reply_markup=None
    )

    await state.clear()


@router.message(RegisterUser.waiting_for_photo)
async def wrong_photo_format(message: Message):
    """Handle non-photo messages"""
    await message.answer(
        "❌ Iltimos, <b>rasm</b> yuboring!\n\n"
        "Matn yoki boshqa fayl emas, faqat rasm."
    )