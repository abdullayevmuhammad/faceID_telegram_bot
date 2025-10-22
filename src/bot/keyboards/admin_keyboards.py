from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def admin_main_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Statistika", callback_data="users_stats")],
        [InlineKeyboardButton(text="⬅️ Chiqish", callback_data="admin_exit")]
    ])
