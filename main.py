
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from app.config import BOT_TOKEN
from app.handlers.start import router
from app.database.db import init_db, close_db


async def main():
    logging.basicConfig(level=logging.INFO)

    # Инициализация базы данных
    await init_db()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Подключение обработчиков
    dp.include_router(router)

    # Команды Telegram
    await bot.set_my_commands([
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="help", description="Помощь"),
    ])

    print("StudyMate запущен!")

    try:
        await dp.start_polling(bot)
    finally:
        await close_db()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
