
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from sqlalchemy import select

from app.database.db import async_session
from app.database.models import Course, Module
from app.states.course_states import AddCourse


router = Router()


@router.message(F.text == "📚 Мои курсы")
async def show_courses(message: Message):
    async with async_session() as session:
        result = await session.execute(
            select(Course)
            .where(Course.user_id == message.from_user.id)
            .order_by(Course.created_at.desc())
        )
        courses = result.scalars().all()

    if not courses:
        await message.answer(
            "📚 У тебя пока нет курсов.\n\n"
            "Нажми «➕ Добавить курс», чтобы создать первый."
        )
        return

    for course in courses:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="📂 Открыть курс",
                        callback_data=f"course_open:{course.id}",
                    )
                ]
            ]
        )

        text = f"📘 {course.title}\n"

        if course.provider:
            text += f"🏫 Платформа: {course.provider}\n"

        if course.url:
            text += f"🔗 Ссылка: {course.url}\n"

        status = "Активен" if course.status == "active" else course.status
        text += f"Статус: {status}"

        await message.answer(text, reply_markup=keyboard)


@router.callback_query(F.data.startswith("course_open:"))
async def open_course(callback: CallbackQuery):
    course_id = int(callback.data.split(":")[1])

    async with async_session() as session:
        result = await session.execute(
            select(Course).where(
                Course.id == course_id,
                Course.user_id == callback.from_user.id,
            )
        )
        course = result.scalar_one_or_none()

        if course is None:
            await callback.answer("Курс не найден.", show_alert=True)
            return

        modules_result = await session.execute(
            select(Module)
            .where(
                Module.course_id == course.id,
                Module.user_id == callback.from_user.id,
            )
            .order_by(Module.position, Module.id)
        )
        modules = modules_result.scalars().all()

    text = f"📘 Курс: {course.title}\n\n"

    if course.description:
        text += f"📝 {course.description}\n\n"

    if not modules:
        text += "В этом курсе пока нет модулей."
    else:
        text += "📚 Модули курса:\n\n"
        for index, module in enumerate(modules, start=1):
            text += f"{index}. {module.title}\n"

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="➕ Добавить модуль",
                    callback_data=f"module_add:{course.id}",
                )
            ]
        ]
    )

    await callback.message.answer(text, reply_markup=keyboard)
    await callback.answer()


@router.message(F.text == "➕ Добавить курс")
async def add_course_start(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(AddCourse.title)

    await message.answer(
        "➕ Добавляем новый курс!\n\n"
        "Напиши название курса:"
    )


@router.message(AddCourse.title)
async def add_course_title(message: Message, state: FSMContext):
    title = (message.text or "").strip()

    if not title:
        await message.answer("Название не может быть пустым. Попробуй ещё раз:")
        return

    if len(title) > 200:
        await message.answer("Название слишком длинное. Максимум 200 символов:")
        return

    await state.update_data(title=title)
    await state.set_state(AddCourse.provider)

    await message.answer(
        "🏫 На какой платформе находится курс?\n\n"
        "Например: Stepik, Udemy, YouTube.\n"
        "Если платформы нет, напиши «Пропустить»."
    )


@router.message(AddCourse.provider)
async def add_course_provider(message: Message, state: FSMContext):
    provider = (message.text or "").strip()

    if not provider:
        await message.answer("Напиши платформу или «Пропустить».")
        return

    if len(provider) > 100:
        await message.answer("Слишком длинное название платформы. Максимум 100 символов:")
        return

    await state.update_data(
        provider=None if provider.lower() == "пропустить" else provider
    )
    await state.set_state(AddCourse.url)

    await message.answer(
        "🔗 Пришли ссылку на курс.\n\n"
        "Или напиши «Пропустить»."
    )


@router.message(AddCourse.url)
async def add_course_url(message: Message, state: FSMContext):
    url = (message.text or "").strip()

    if not url:
        await message.answer("Пришли ссылку или напиши «Пропустить».")
        return

    if url.lower() == "пропустить":
        url = None
    elif len(url) > 500 or not url.startswith(("http://", "https://")):
        await message.answer(
            "Похоже, ссылка некорректна.\n"
            "Пришли ссылку, начинающуюся с http:// или https://,\n"
            "или напиши «Пропустить»."
        )
        return

    await state.update_data(url=url)
    await state.set_state(AddCourse.description)

    await message.answer(
        "📝 Добавь описание курса.\n\n"
        "Например: «Основы Linux и администрирования».\n"
        "Или напиши «Пропустить»."
    )


@router.message(AddCourse.description)
async def add_course_description(message: Message, state: FSMContext):
    description = (message.text or "").strip()

    if not description:
        await message.answer("Напиши описание или «Пропустить».")
        return

    if len(description) > 4000:
        await message.answer("Описание слишком длинное. Максимум 4000 символов:")
        return

    data = await state.get_data()

    course = Course(
        user_id=message.from_user.id,
        title=data["title"],
        provider=data.get("provider"),
        url=data.get("url"),
        description=(
            None if description.lower() == "пропустить" else description
        ),
        status="active",
    )

    try:
        async with async_session() as session:
            session.add(course)
            await session.commit()
    except Exception:
        await state.clear()
        await message.answer(
            "Не удалось сохранить курс. Попробуй ещё раз позже."
        )
        raise

    await state.clear()

    await message.answer(
        "✅ Курс успешно добавлен!\n\n"
        f"📘 Название: {course.title}\n"
        f"🏫 Платформа: {course.provider or 'Не указана'}\n"
        f"🔗 Ссылка: {course.url or 'Не указана'}\n"
        f"📝 Описание: {course.description or 'Нет'}"
    )
