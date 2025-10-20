from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def user_main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🪪 Ro'yxatdan o'tish")],
            [KeyboardButton(text="👤 Profilim"), KeyboardButton(text="🔄 Ma'lumotni yangilash")],
            [KeyboardButton(text="ℹ️ Yordam")],
        ],
        resize_keyboard=True
    )

def admin_main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🪪 Ro'yxatdan o'tish")],
            [KeyboardButton(text="👤 Profilim"), KeyboardButton(text="🔄 Ma'lumotni yangilash")],
            [KeyboardButton(text="📊 Admin panel")],
            [KeyboardButton(text="ℹ️ Yordam")],
        ],
        resize_keyboard=True
    )
