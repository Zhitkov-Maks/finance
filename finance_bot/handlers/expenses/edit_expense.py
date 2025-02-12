import asyncio

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.markdown import hbold

from api.common import edit_object, get_full_info
from handlers.decorator_handler import decorator_errors
from keyboards.expenses import choice_expense_edit
from keyboards.incomes import get_action
from keyboards.keyboards import cancel_
from states.expenses import EditExpenseState, ExpensesState
from utils.accounts import is_valid_balance
from utils.common import remove_message_after_delay
from utils.expenses import (
    create_new_expenses_data,
    generate_message_expense_info,
    expense_url_by_id,
)

exp_edit_router: Router = Router()


@exp_edit_router.callback_query(F.data == "edit_expense")
async def edit_expense_choice(callback: CallbackQuery) -> None:
    """A handler for selecting an expense editing option."""
    await callback.message.edit_text(
        text=hbold("Выберите вариант редактирования."),
        reply_markup=choice_expense_edit,
        parse_mode="HTML",
    )


@exp_edit_router.callback_query(F.data == "edit_expense_balance")
async def edit_balance(callback: CallbackQuery, state: FSMContext) -> None:
    """
    The handler for requesting the amount of expense when editing only
    the balance.
    """
    await state.set_state(EditExpenseState.amount)
    await state.update_data(method="PATCH")
    await callback.message.edit_text(
        text=hbold("Введите новую сумму расхода."),
        reply_markup=cancel_,
        parse_mode="HTML",
    )


@exp_edit_router.message(EditExpenseState.amount)
@decorator_errors
async def edit_expense_request(message: Message, state: FSMContext) -> None:
    """The final handler for editing."""
    data: dict[str, str | int] = await state.get_data()
    expense_id, usr_id = data["expense_id"], message.from_user.id
    method: str = data.get("method", "PUT")
    url: str = await expense_url_by_id(expense_id)
    if not is_valid_balance(message.text):
        err_mess: Message = await message.answer(
            "Неверный формат ввода, попробуйте еще раз.", reply_markup=cancel_
        )
        asyncio.create_task(remove_message_after_delay(60, err_mess))
        return

    if method == "PATCH":
        edit_data: dict = {"amount": float(message.text)}

    else:
        edit_data: dict[str, str | float | int] = await create_new_expenses_data(
            data, float(message.text)
        )

    await edit_object(url, usr_id, edit_data, method)
    response: dict[str, int | str | dict[str, int | str]] = await get_full_info(
        url, usr_id
    )

    text: str = await generate_message_expense_info(response)
    await state.set_state(ExpensesState.action)
    await message.answer(
        text=hbold(text),
        parse_mode="HTML",
        reply_markup=await get_action(),
    )
    asyncio.create_task(remove_message_after_delay(60, message))
