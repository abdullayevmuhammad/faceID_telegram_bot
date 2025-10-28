# src/bot/states/admin_states.py
from aiogram.fsm.state import StatesGroup, State

class AdminManage(StatesGroup):
    adding_admin_wait_id = State()
    removing_admin_wait_id = State()
    edit_user_wait_passport = State()
    edit_user_wait_photo = State()
    add_user_wait_passport = State()
    add_user_wait_photo = State()
