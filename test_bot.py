
import asyncio

from aiogram import Bot
from app.config import BOT_TOKEN


async def main():
    bot = Bot(token=BOT_TOKEN)

    try:
        me = await bot.get_me()

        print("Подключение успешно!")
        print("Имя бота:", me.full_name)
        print("Username:", me.username)

    except Exception as error:
        print("Ошибка подключения:", repr(error))

    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
