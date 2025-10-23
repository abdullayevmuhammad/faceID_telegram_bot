from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def cancel_keyboard() -> ReplyKeyboardMarkup:
    """Bekor qilish uchun universal klaviatura"""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Bekor qilish")]],
        resize_keyboard=True
    )

def main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Asosiy menyu"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🪪 Ro'yxatdan o'tish")],
            [KeyboardButton(text="👤 Profilim"), KeyboardButton(text="🔄 Ma'lumotni yangilash")],
            [KeyboardButton(text="ℹ️ Yordam")]
        ],
        resize_keyboard=True
    )
