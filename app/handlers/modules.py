
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from sqlalchemy import select, func

from app.database.db import async_session
from app.database.models import Course, Module
from app.states.module_states import AddModule


router = Router()


def module_keyboard(module_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📂 Открыть",
                    callback_data=f"module_open:{module_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="➕ Добавить подмодуль",
                    callback_data=f"module_add_child:{module_id}",
                )
            ],
        ]
    )


@router.callback_query(F.data.startswith("module_add:"))
async def add_module_start(
    callback: CallbackQuery,
    state: FSMContext,
):
    course_id = int(callback.data.split(":")[1])

    async with async_session() as session:
        course = await session.scalar(
            select(Course).where(
                Course.id == course_id,
                Course.user_id == callback.from_user.id,
            )
        )

    if not course:
        await callback.answer("Курс не найден.", show_alert=True)
        return

    await state.clear()
    await state.update_data(
        course_id=course_id,
        parent_id=None,
    )
    await state.set_state(AddModule.title)

    await callback.message.answer(
        f"➕ Добавляем модуль в курс «{course.title}».\n\n"
        "Напиши название модуля:"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("module_add_child:"))
async def add_child_start(
    callback: CallbackQuery,
    state: FSMContext,
):
    parent_id = int(callback.data.split(":")[1])

    async with async_session() as session:
        parent = await session.scalar(
            select(Module).where(
                Module.id == parent_id,
                Module.user_id == callback.from_user.id,
            )
        )

    if not parent:
        await callback.answer("Модуль не найден.", show_alert=True)
        return

    await state.clear()
    await state.update_data(
        course_id=parent.course_id,
        parent_id=parent.id,
    )
    await state.set_state(AddModule.title)

    await callback.message.answer(
        f"➕ Добавляем подмодуль внутрь «{parent.title}».\n\n"
        "Напиши название:"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("module_open:"))
async def open_module(callback: CallbackQuery):
    module_id = int(callback.data.split(":")[1])

    async with async_session() as session:
        module = await session.scalar(
            select(Module).where(
                Module.id == module_id,
                Module.user_id == callback.from_user.id,
            )
        )

        if not module:
            await callback.answer("Модуль не найден.", show_alert=True)
            return

        children = (
            await session.scalars(
                select(Module)
                .where(
                    Module.parent_id == module.id,
                    Module.user_id == callback.from_user.id,
                )
                .order_by(Module.position, Module.id)
            )
        ).all()

        title = module.title
        child_data = [
            (child.id, child.title)
            for child in children
        ]

    if not child_data:
        text = f"📂 {title}\n\nПодмодулей пока нет."
    else:
        text = f"📂 {title}\n\nПодмодули:"

    await callback.message.answer(text)

    for child_id, child_title in child_data:
        await callback.message.answer(
            f"📁 {child_title}",
            reply_markup=module_keyboard(child_id),
        )

    await callback.message.answer(
        "Можешь добавить новый подмодуль:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="➕ Добавить подмодуль",
                        callback_data=f"module_add_child:{module_id}",
                    )
                ]
            ]
        ),
    )

    await callback.answer()


@router.message(AddModule.title)
async def add_module_finish(
    message: Message,
    state: FSMContext,
):
    title = (message.text or "").strip()

    if not title:
        await message.answer("Название не может быть пустым.")
        return

    if len(title) > 200:
        await message.answer("Максимум 200 символов.")
        return

    data = await state.get_data()

    course_id = data.get("course_id")
    parent_id = data.get("parent_id")

    async with async_session() as session:
        course = await session.scalar(
            select(Course).where(
                Course.id == course_id,
                Course.user_id == message.from_user.id,
            )
        )

        if not course:
            await state.clear()
            await message.answer("Курс не найден.")
            return

        if parent_id is not None:
            parent = await session.scalar(
                select(Module).where(
                    Module.id == parent_id,
                    Module.course_id == course_id,
                    Module.user_id == message.from_user.id,
                )
            )

            if not parent:
                await state.clear()
                await message.answer("Родительский модуль не найден.")
                return

        last_position = await session.scalar(
            select(func.max(Module.position)).where(
                Module.course_id == course_id,
                Module.parent_id == parent_id,
                Module.user_id == message.from_user.id,
            )
        )

        new_module = Module(
            user_id=message.from_user.id,
            course_id=course_id,
            parent_id=parent_id,
            title=title,
            position=(last_position or 0) + 1,
            status="not_started",
        )

        session.add(new_module)
        await session.commit()

    await state.clear()

    await message.answer(
        f"✅ {'Подмодуль' if parent_id else 'Модуль'} добавлен!\n\n"
        f"📁 {title}"
    )
