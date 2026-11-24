
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📚 Мои курсы"),
            KeyboardButton(text="➕ Добавить курс"),
        ],
        [
            KeyboardButton(text="📝 Мои задания"),
            KeyboardButton(text="🛠 Мои проекты"),
        ],
        [
            KeyboardButton(text="⏱ Учебные сессии"),
            KeyboardButton(text="📊 Мой прогресс"),
        ],
        [
            KeyboardButton(text="⚙️ Настройки"),
        ],
    ],
    resize_keyboard=True,
)
