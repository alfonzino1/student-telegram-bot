
from datetime import datetime

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.states.task_states import AddTask
from app.database.db import async_session
from app.database.models import Task
from app.keyboards.task_actions import task_actions_keyboard
from aiogram.types import CallbackQuery
from sqlalchemy import select

router = Router()


@router.message(F.text == "➕ Добавить задание")
async def add_task_start(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(AddTask.title)

    await message.answer(
        "➕ Давай добавим новое задание!\n\n"
        "Напиши его название:"
    )


@router.message(AddTask.title)
async def add_task_title(message: Message, state: FSMContext):
    title = (message.text or "").strip()

    if not title:
        await message.answer("Название не может быть пустым. Попробуй ещё раз:")
        return

    if len(title) > 200:
        await message.answer("Название слишком длинное. Максимум 200 символов:")
        return

    await state.update_data(title=title)
    await state.set_state(AddTask.subject)

    await message.answer(
        "📚 По какому предмету это задание?\n\n"
        "Если предмет не нужен, напиши «Пропустить»."
    )


@router.message(AddTask.subject)
async def add_task_subject(message: Message, state: FSMContext):
    subject = (message.text or "").strip()

    if not subject:
        await message.answer("Напиши название предмета или «Пропустить».")
        return

    await state.update_data(
        subject=None if subject.lower() == "пропустить" else subject
    )
    await state.set_state(AddTask.description)

    await message.answer(
        "📝 Добавь описание задания.\n\n"
        "Или напиши «Пропустить»."
    )


@router.message(AddTask.description)
async def add_task_description(message: Message, state: FSMContext):
    description = (message.text or "").strip()

    if not description:
        await message.answer("Напиши описание или «Пропустить».")
        return

    await state.update_data(
        description=None if description.lower() == "пропустить" else description
    )
    await state.set_state(AddTask.due_date)

    await message.answer(
        "📅 Когда нужно выполнить задание?\n\n"
        "Напиши дату и время в формате:\n"
        "25.11.2026 18:00\n\n"
        "Или напиши «Пропустить»."
    )


@router.message(AddTask.due_date)
async def add_task_due_date(message: Message, state: FSMContext):
    date_text = (message.text or "").strip()

    if not date_text:
        await message.answer("Напиши дату или «Пропустить».")
        return

    due_at = None

    if date_text.lower() != "пропустить":
        try:
            due_at = datetime.strptime(
                date_text, "%d.%m.%Y %H:%M"
            )
        except ValueError:
            await message.answer(
                "Не удалось распознать дату.\n"
                "Используй формат: 25.11.2026 18:00\n"
                "Или напиши «Пропустить»."
            )
            return

        if due_at <= datetime.now():
            await message.answer(
                "Эта дата уже прошла. Укажи будущую дату и время."
            )
            return

    data = await state.get_data()

    try:
        async with async_session() as session:
            task = Task(
                user_id=message.from_user.id,
                title=data["title"],
                description=data.get("description"),
                due_at=due_at,
                status="pending",
            )

            session.add(task)
            await session.commit()

    except Exception:
        await message.answer(
            "Не удалось сохранить задание. Попробуй ещё раз позже."
        )
        await state.clear()
        raise

    await state.clear()

    due_text = (
        due_at.strftime("%d.%m.%Y в %H:%M")
        if due_at else "Не указан"
    )

    await message.answer(
        "✅ Задание успешно сохранено!\n\n"
        f"📌 Название: {data['title']}\n"
        f"📚 Предмет: {data.get('subject') or 'Не указан'}\n"
        f"📝 Описание: {data.get('description') or 'Нет'}\n"
        f"📅 Срок: {due_text}"
    )


@router.message(F.text == "📚 Мои задания")
async def show_tasks(message: Message):
    async with async_session() as session:
        result = await session.execute(
            select(Task)
            .where(Task.user_id == message.from_user.id)
            .order_by(Task.due_at.is_(None), Task.due_at)
        )

        tasks = result.scalars().all()

    if not tasks:
        await message.answer(
            "📚 У тебя пока нет заданий.\n\n"
            "Нажми «➕ Добавить задание», чтобы создать первое!"
        )
        return

    await message.answer("📚 Твои задания:")

    for task in tasks:
        status = (
            "✅ Выполнено"
            if task.status == "completed"
            else "🕓 В процессе"
        )

        due = (
            task.due_at.strftime("%d.%m.%Y в %H:%M")
            if task.due_at
            else "Не указан"
        )

        text = (
            f"📌 {task.title}\n"
            f"Статус: {status}\n"
            f"Срок: {due}"
        )

        if task.description:
            text += f"\nОписание: {task.description}"

        await message.answer(
            text,
            reply_markup=task_actions_keyboard(task.id, task.status)
        )


@router.callback_query(F.data.startswith("task_done:"))
async def complete_task(callback: CallbackQuery):
    task_id = int(callback.data.split(":")[1])

    async with async_session() as session:
        result = await session.execute(
            select(Task).where(
                Task.id == task_id,
                Task.user_id == callback.from_user.id
            )
        )
        task = result.scalar_one_or_none()

        if task is None:
            await callback.answer("Задание не найдено.", show_alert=True)
            return

        task.status = "completed"
        await session.commit()

    await callback.message.edit_text(
        f"✅ Задание выполнено!\n\n📌 {task.title}"
    )
    await callback.answer("Статус обновлён!")


@router.callback_query(F.data.startswith("task_delete:"))
async def delete_task(callback: CallbackQuery):
    task_id = int(callback.data.split(":")[1])

    async with async_session() as session:
        result = await session.execute(
            select(Task).where(
                Task.id == task_id,
                Task.user_id == callback.from_user.id
            )
        )
        task = result.scalar_one_or_none()

        if task is None:
            await callback.answer("Задание не найдено.", show_alert=True)
            return

        await session.delete(task)
        await session.commit()

    await callback.message.edit_text("🗑 Задание удалено.")
    await callback.answer("Удалено!")
