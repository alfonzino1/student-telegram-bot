
import asyncio

from aiogram import Bot
from aiogram.types import BotCommand

from app.config import BOT_TOKEN


async def main():
    bot = Bot(token=BOT_TOKEN)

    try:
        me = await bot.get_me()
        print("Подключение успешно:", me.username)

        result = await bot.set_my_commands([
            BotCommand(command="start", description="Запустить бота"),
            BotCommand(command="help", description="Помощь"),
        ])

        print("Регистрация команд:", result)

    except Exception as error:
        print("Ошибка:", repr(error))

    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
