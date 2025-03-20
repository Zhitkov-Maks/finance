from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from keyboards.keyboards import main_menu
from handlers.decorator_handler import decorator_errors

invalid_router = Router()


@invalid_router.message(F.text)
@decorator_errors
async def invalid_message_text(message: Message, state: FSMContext) -> None:
    """A handler for unfamiliar text commands."""
    await state.clear()
    await message.answer(
        text="Ошибка ввода. Будьте внимательнее и попробуйте сначала.",
        reply_markup=main_menu
    )


@invalid_router.callback_query(F.data)
@decorator_errors
async def invalid_callback(callback: CallbackQuery, state: FSMContext) -> None:
    """A handler for buttons that don't have any actions."""
    await callback.answer(
        text="Я не могу вам ничего показать, \
            так как на мне нет никаких данных.",
        show_alert=True
    )
