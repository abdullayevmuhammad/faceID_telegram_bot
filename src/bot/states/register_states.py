# src/bot/states/register_states.py
from aiogram.fsm.state import StatesGroup, State

class RegisterUser(StatesGroup):
    waiting_for_passport = State()
    waiting_for_photo = State()
