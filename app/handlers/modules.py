
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select

from app.database.db import async_session
from app.database.models import Course, Module
from app.states.module_states import AddModule


router = Router()


@router.callback_query(F.data.startswith("module_add:"))
async def add_module_start(callback: CallbackQuery, state: FSMContext):
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

    await state.clear()
    await state.update_data(course_id=course_id)
    await state.set_state(AddModule.title)

    await callback.message.answer(
        f"➕ Добавляем модуль в курс «{course.title}».\n\n"
        "Напиши название модуля:"
    )
    await callback.answer()


@router.message(AddModule.title)
async def add_module_title(message: Message, state: FSMContext):
    title = (message.text or "").strip()

    if not title:
        await message.answer("Название не может быть пустым. Попробуй ещё раз:")
        return

    if len(title) > 200:
        await message.answer("Название слишком длинное. Максимум 200 символов:")
        return

    data = await state.get_data()
    course_id = data.get("course_id")

    try:
        async with async_session() as session:
            course_result = await session.execute(
                select(Course).where(
                    Course.id == course_id,
                    Course.user_id == message.from_user.id,
                )
            )
            course = course_result.scalar_one_or_none()

            if course is None:
                await state.clear()
                await message.answer("Курс не найден. Открой список курсов заново.")
                return

            last_module_result = await session.execute(
                select(Module)
                .where(
                    Module.course_id == course_id,
                    Module.user_id == message.from_user.id,
                )
                .order_by(Module.position.desc())
                .limit(1)
            )
            last_module = last_module_result.scalar_one_or_none()

            next_position = (
                last_module.position + 1 if last_module else 1
            )

            module = Module(
                user_id=message.from_user.id,
                course_id=course_id,
                title=title,
                position=next_position,
                status="not_started",
            )

            session.add(module)
            await session.commit()

            course_title = course.title

    except Exception:
        await state.clear()
        await message.answer(
            "Не удалось сохранить модуль. Попробуй ещё раз позже."
        )
        raise

    await state.clear()

    await message.answer(
        "✅ Модуль успешно добавлен!\n\n"
        f"📘 Курс: {course_title}\n"
        f"📚 Модуль: {title}"
    )
