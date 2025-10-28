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
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from utils.db import is_admin


def get_main_menu(telegram_id: int) -> ReplyKeyboardMarkup:
    """Foydalanuvchi roliga qarab asosiy menyu shakllantiradi"""
    if is_admin(telegram_id):
        # 👑 Admin uchun
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="🪪 Ro'yxatdan o'tish")],
                [KeyboardButton(text="👤 Profilim"), KeyboardButton(text="🔄 Ma'lumotni yangilash")],
                [KeyboardButton(text="📊 Admin panel")],
                [KeyboardButton(text="ℹ️ Yordam")]
            ],
            resize_keyboard=True
        )
    else:
        # 👤 Oddiy foydalanuvchi uchun
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="🪪 Ro'yxatdan o'tish")],
                [KeyboardButton(text="👤 Profilim"), KeyboardButton(text="🔄 Ma'lumotni yangilash")],
                [KeyboardButton(text="ℹ️ Yordam")]
            ],
            resize_keyboard=True
        )
