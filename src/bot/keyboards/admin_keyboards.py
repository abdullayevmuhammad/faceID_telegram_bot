# bot/keyboards/admin_keyboards.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def admin_main_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Statistika", callback_data="users_stats")],
        [InlineKeyboardButton(text="👑 Adminlar ro‘yxati", callback_data="admin_list")],
        [InlineKeyboardButton(text="➕ Yangi admin qo‘shish", callback_data="add_admin")],
        [InlineKeyboardButton(text="🗑 Adminni olib tashlash", callback_data="remove_admin")],
        [InlineKeyboardButton(text="🧍‍♂️ Foydalanuvchini o‘zgartirish", callback_data="edit_user")],
        [InlineKeyboardButton(text="➕ User qo‘shish", callback_data="add_user")],
        [InlineKeyboardButton(text="⬅️ Chiqish", callback_data="admin_exit")]
    ])
