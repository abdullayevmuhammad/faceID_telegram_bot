# src/bot/states/update_states.py
from aiogram.fsm.state import StatesGroup, State

class UpdateUser(StatesGroup):
    waiting_for_update = State()
