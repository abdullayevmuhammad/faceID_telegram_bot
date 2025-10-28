# src/bot/states/admin_states.py
from aiogram.fsm.state import StatesGroup, State

class AdminManage(StatesGroup):
    add_user_wait_passport = State()
    add_user_wait_photo = State()

    edit_user_wait_passport = State()
    edit_user_wait_photo = State()

    delete_user_wait_passport = State()

    adding_admin_wait_id = State()
    removing_admin_wait_id = State()
