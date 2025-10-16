# src/bot/handlers/update_photo.py
import re
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from bot.states.update_states import UpdateUser
from utils.storage import user_storage
from bot.keyboards.user_keyboards import cancel_keyboard

router = Router()


@router.message(Command("update"))
async def start_update(message: Message, state: FSMContext):
    """Start profile update"""
    user = user_storage.get_user_by_telegram_id(message.from_user.id)

    if not user:
        await message.answer(
            "❌ Siz hali ro'yxatdan o'tmagansiz!\n\n"
            "Avval ro'yxatdan o'ting: /register"
        )
        return

    text = (
        "🔄 <b>Ma'lumotlarni yangilash</b>\n\n"
        "Nimani yangilashni xohlaysiz?\n\n"
        "1️⃣ Pasport raqami\n"
        "2️⃣ Rasm\n\n"
        "Yangi <b>pasport raqamini</b> yuboring yoki\n"
        "Yangi <b>rasmni</b> yuboring:"
    )

    await message.answer(text, reply_markup=cancel_keyboard())
    await state.set_state(UpdateUser.waiting_for_update)


@router.message(UpdateUser.waiting_for_update, F.text == "❌ Bekor qilish")
async def cancel_update(message: Message, state: FSMContext):
    """Cancel update"""
    await state.clear()
    await message.answer("❌ Yangilash bekor qilindi.", reply_markup=None)


@router.message(UpdateUser.waiting_for_update, F.photo)
async def update_photo(message: Message, state: FSMContext):
    """Update user photo"""
    user = user_storage.get_user_by_telegram_id(message.from_user.id)

    if not user:
        await message.answer("❌ Xatolik yuz berdi!")
        await state.clear()
        return

    # Get new photo
    new_photo_id = message.photo[-1].file_id

    # Update user
    user_storage.add_user(
        telegram_id=user['telegram_id'],
        full_name=user['full_name'],
        passport=user['passport'],
        photo_id=new_photo_id
    )

    await message.answer(
        "✅ <b>Rasm muvaffaqiyatli yangilandi!</b>\n\n"
        "📸 Yangi rasmingiz saqlandi.",
        reply_markup=None