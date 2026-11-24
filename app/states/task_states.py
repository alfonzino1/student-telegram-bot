
from aiogram.fsm.state import State, StatesGroup


class AddTask(StatesGroup):
    title = State()
    subject = State()
    description = State()
    due_date = State()

