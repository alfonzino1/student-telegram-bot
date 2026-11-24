
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def task_actions_keyboard(task_id: int, status: str):
    buttons = []

    if status != "completed":
        buttons.append([
            InlineKeyboardButton(
                text="✅ Выполнено",
                callback_data=f"task_done:{task_id}"
            )
        ])

    buttons.append([
        InlineKeyboardButton(
            text="🗑 Удалить",
            callback_data=f"task_delete:{task_id}"
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)
