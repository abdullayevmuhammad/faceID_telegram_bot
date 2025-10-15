# src/main.py
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from bot.handlers import start
from bot.handlers import register_user
from bot.handlers import admin_panel

BOT_TOKEN = '8363824683:AAEzNvWQox8ALDQI3MKemZVpK3IvGNhtfgE'
# from bot.config import BOT_TOKEN
# from bot.handlers import start, register_user, check_user, admin_panel

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s",
)

async def main():
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=MemoryStorage())

    # # Handlers
    # dp.include_router(start.router)
    # dp.include_router(register_user.router)
    # dp.include_router(check_user.router)
    # dp.include_router(admin_panel.router)

    logging.info("🤖 Bot started successfully...")
    await bot.delete_webhook(drop_pending_updates=True)

    dp.include_router(start.router)
    dp.include_router(register_user.router)
    dp.include_router(admin_panel.router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
