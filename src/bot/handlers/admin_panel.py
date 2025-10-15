# src/bot/handlers/admin_panel.py
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from sqlalchemy import select, func
from database.models import User
from database.session import AsyncSessionLocal
from datetime import datetime, date
import os
from dotenv import load_dotenv
load_dotenv()
router = Router()

ADMIN_ID = int(os.getenv("ADMIN_ID"))  # 🔒 bu yerga o‘zingning Telegram ID’ingni yoz

def is_admin(message: Message) -> bool:
    return message.from_user.id == ADMIN_ID


@router.message(Command("admin"))
async def admin_panel(message: Message):
    if not is_admin(message):
        await message.answer("🚫 Sizda bu buyruqdan foydalanish huquqi yo‘q.")
        return

    async with AsyncSessionLocal() as session:
        # jami foydalanuvchilar
        total_users = (await session.execute(select(func.count()).select_from(User))).scalar()

        # bugun qo‘shilganlar
        today = date.today()
        today_users = (
            await session.execute(
                select(func.count()).select_from(User).where(func.date(User.created_at) == today)
            )
        ).scalar()

        # passport bo‘yicha duplicateni topish
        duplicates = (
            await session.execute(
                select(User.passport, func.count(User.passport))
                .group_by(User.passport)
                .having(func.count(User.passport) > 1)
            )
        ).all()

        dup_count = len(duplicates)

    text = (
        "<b>📊 Face ID Tizimi Statistikasi</b>\n\n"
        f"👥 Jami foydalanuvchilar: <b>{total_users}</b>\n"
        f"🗓️ Bugun qo‘shilganlar: <b>{today_users}</b>\n"
        f"🔁 Duplicate foydalanuvchilar: <b>{dup_count}</b>\n"
    )

    await message.answer(text)
