
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📚 Мои задания"),
            KeyboardButton(text="📅 Расписание"),
        ],
        [
            KeyboardButton(text="➕ Добавить задание"),
            KeyboardButton(text="📊 Моя статистика"),
        ],
        [
            KeyboardButton(text="⚙️ Настройки"),
        ],
    ],
    resize_keyboard=True
)
