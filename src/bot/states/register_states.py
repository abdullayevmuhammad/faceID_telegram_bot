# src/bot/states/register_states.py
from aiogram.fsm.state import State, StatesGroup

class RegisterUser(StatesGroup):
    waiting_for_passport = State()      # 🪪 Pasportni kiritish
    waiting_for_photo = State()         # 📸 Rasm yuborish
    waiting_for_update_choice = State() # 🔄 Mavjud foydalanuvchi uchun tanlov
