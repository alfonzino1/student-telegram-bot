
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.keyboards.main_menu import main_menu

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(
        "Привет! 🌷\n\n"
        "Я StudyMate — твой личный учебный помощник.\n\n"
        "Моя задача — помочь тебе не забывать "
        "об учёбе, организовать занятия и "
        "следить за твоим прогрессом.\n\n"
        "Давай начнём! Выбери нужный раздел:",
        reply_markup=main_menu
    )


@router.message(lambda message: message.text == "⚙️ Настройки")
async def settings_handler(message: Message):
    await message.answer(
        "⚙️ Настройки пока находятся в разработке."
    )
