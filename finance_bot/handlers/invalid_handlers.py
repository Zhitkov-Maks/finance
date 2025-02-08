from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from keyboards.keyboards import main_menu

invalid_router = Router()


@invalid_router.message(F.text)
async def invalid_message_text(message: Message, state: FSMContext) -> None:
    """A handler for unfamiliar text commands."""
    await state.clear()
    await message.answer(
        text="Ошибка ввода. Будьте внимательнее и попробуйте сначала.",
        reply_markup=main_menu
    )


@invalid_router.callback_query(F.data)
async def invalid_callback(callback: CallbackQuery) -> None:
    """A handler for buttons that don't have any actions."""
    await callback.answer(text="Я не могу вам ничего показать, так как "
                               "на мне нет никаких данных.")
