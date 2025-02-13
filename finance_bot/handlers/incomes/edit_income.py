from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.markdown import hbold

from api.common import edit_object, get_full_info
from handlers.decorator_handler import decorator_errors
from keyboards.incomes import choice_edit, get_action
from keyboards.keyboards import cancel_
from states.incomes import EditIncomesState, IncomesState
from utils.accounts import is_valid_balance
from utils.incomes import (
    incomes_by_id,
    generate_message_income_info,
    create_new_incomes_data
)

inc_edit_router = Router()


@inc_edit_router.callback_query(F.data == "edit_income")
async def edit_income_choice(callback: CallbackQuery) -> None:
    """A handler for selecting an income editing option."""
    text = "Выберите вариант редактирования."
    await callback.message.edit_text(
        text=hbold(text),
        reply_markup=choice_edit,
        parse_mode="HTML"
    )


@inc_edit_router.callback_query(F.data == "edit_income_balance")
async def edit_balance(callback: CallbackQuery, state: FSMContext) -> None:
    """
    The handler for requesting the amount of income when editing only
    the balance.
    """
    await state.set_state(EditIncomesState.amount)
    await state.update_data(method="PATCH")
    await callback.message.edit_text(
        text=hbold("Введите новую сумму дохода."),
        reply_markup=cancel_,
        parse_mode="HTML"
    )


@inc_edit_router.message(EditIncomesState.amount)
@decorator_errors
async def edit_income_request(message: Message, state: FSMContext) -> None:
    """The final handler for editing."""
    data: dict[str, str | int] = await state.get_data()
    income_id, usr_id = data["income_id"], message.from_user.id
    method: str = data.get("method", "PUT")
    url: str = await incomes_by_id(income_id)

    if not is_valid_balance(message.text):
        await message.answer(
            "Invalid balance format. Please enter a valid number.", reply_markup=cancel_
        )
        return

    if method == "PATCH":
        edit_data: dict = {"amount": float(message.text)}

    else:
        edit_data: dict[str, str | float | int] = await create_new_incomes_data(
        data, float(message.text)
    )

    await edit_object(url, usr_id, edit_data, method)
    response: dict[str, int | str | dict[str, int | str]] = \
        await get_full_info(url, usr_id)

    text: str = await generate_message_income_info(response)
    await state.set_state(IncomesState.action)
    await message.answer(
        text=hbold(text),
        parse_mode="HTML",
        reply_markup=await get_action(),
    )
