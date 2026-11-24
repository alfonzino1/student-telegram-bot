
from aiogram.fsm.state import State, StatesGroup


class AddCourse(StatesGroup):
    title = State()
    provider = State()
    url = State()
    description = State()
