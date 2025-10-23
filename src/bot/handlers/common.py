from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from bot.keyboards.user_keyboards import main_menu_keyboard

router = Router()

@router.message(F.text == "❌ Bekor qilish")
async def cancel_process(message: Message, state: FSMContext):
    """Har qanday jarayonni bekor qiladi"""
    current_state = await state.get_state()
    if current_state is None:
        return await message.answer("Hech qanday jarayon faol emas.", reply_markup=main_menu_keyboard())

    await state.clear()
    await message.answer("❌ Amal bekor qilindi. Asosiy menyuga qaytdingiz.", reply_markup=main_menu_keyboard())
