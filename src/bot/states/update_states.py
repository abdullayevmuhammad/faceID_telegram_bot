# src/bot/states/update_states.py
from aiogram.fsm.state import State, StatesGroup

class UpdateUser(StatesGroup):
    waiting_for_passport = State()  # 🪪 foydalanuvchi pasport raqamini kiritadi
    waiting_for_photo = State()     # 📸 foydalanuvchi yangi rasm yuboradi
