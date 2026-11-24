
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from app.config import BOT_TOKEN
from app.database.db import init_db, close_db

from app.handlers.start import router as start_router
from app.handlers.tasks import router as tasks_router
from app.handlers.courses import router as courses_router
from app.handlers.modules import router as modules_router
async def main():
    logging.basicConfig(level=logging.INFO)

    await init_db()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(start_router)
    dp.include_router(tasks_router)
    dp.include_router(courses_router)
    dp.include_router(modules_router)

    try:
        await bot.set_my_commands([
            BotCommand(
                command="start",
                description="Запустить бота"
            ),
            BotCommand(
                command="help",
                description="Помощь"
            ),
        ])

        print("StudyMate запущен!")

        await dp.start_polling(bot)

    finally:
        await bot.session.close()
        await close_db()


if __name__ == "__main__":
    asyncio.run(main())
