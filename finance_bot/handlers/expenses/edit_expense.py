from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.markdown import hbold

from api.common import edit_object, get_full_info
from handlers.decorator_handler import decorator_errors
from keyboards.expenses import choice_edit
from keyboards.incomes import get_action
from keyboards.keyboards import cancel_action
from states.expenses import EditExpenseState, ExpensesState
from utils.accounts import is_valid_balance
from utils.expenses import (
    create_new_expenses_data,
    generate_message_expense_info,
    expense_url_by_id,
)

exp_edit_router: Router = Router()


@exp_edit_router.callback_query(F.data == "edit_expense")
@decorator_errors
async def edit_expense_choice(
        callback: CallbackQuery, state: FSMContext
) -> None:
    """A handler for selecting an expense editing option."""
    data: dict = await state.get_data()
    expense_id = data.get("expense_id")
    await state.set_state(ExpensesState.show)
    await callback.message.edit_text(
        text=hbold(
            "Выберите вариант редактирования.\n"
            "✎ - Польностью.\n"
            "₱ - Баланс.\n"
            "㊂ - Меню.\n"
            "🔙 - Назад.\n"
        ),
        reply_markup=await choice_edit(expense_id),
        parse_mode="HTML",
    )


@exp_edit_router.callback_query(F.data == "edit_expense_balance")
@decorator_errors
async def edit_balance(callback: CallbackQuery, state: FSMContext) -> None:
    """
    The handler for requesting the amount of expense when editing only
    the balance.
    """
    await state.set_state(EditExpenseState.comment)
    await state.update_data(method="PATCH")
    await callback.message.edit_text(
        text=hbold("Введите новую сумму расхода."),
        reply_markup=await cancel_action(),
        parse_mode="HTML",
    )


@exp_edit_router.message(EditExpenseState.amount)
@decorator_errors
async def ask_add_comment(message: Message, state: FSMContext) -> None:
    """Handler for the amount and input of the expense comment."""
    show: str = (await state.get_data())["show"]
    if not is_valid_balance(message.text):
        await message.answer(
            "Ошибка ввода, попробуйте еще раз.",
            reply_markup=await cancel_action(show)
        )
        return

    await state.update_data(amount=message.text)
    await state.set_state(EditExpenseState.comment)
    await message.answer(
        text=hbold("Введите комментарий. Если комментарий не нужен, "
                   "то, отправьте один любой символ."),
        reply_markup=await cancel_action(show),
        parse_mode="HTML"
    )


@exp_edit_router.message(EditExpenseState.comment)
@decorator_errors
async def edit_expense_request(message: Message, state: FSMContext) -> None:
    """The final handler for editing."""
    data: dict[str, str | int] = await state.get_data()
    expense_id, usr_id = data["expense_id"], message.from_user.id
    show: str = data["show"]
    url: str = await expense_url_by_id(expense_id)
    method: str = ""

    if data.get("method"):
        method = data.pop("method")
        if not is_valid_balance(message.text):
            await message.answer(
                "Invalid balance format. Please enter a valid number.",
                reply_markup=await cancel_action(show)
            )
            return
        edit_data: dict = {"amount": float(message.text)}

    else:
        comment: str = message.text
        if comment in ["no comment", "no", "нет"] or len(comment) < 3:
            comment = ""
        edit_data: dict = await create_new_expenses_data(data, comment)

    await edit_object(url, usr_id, edit_data, method)
    response: dict = await get_full_info(url, usr_id)

    text: str = await generate_message_expense_info(response)
    await state.set_state(ExpensesState.action)
    await message.answer(
        text=hbold(text),
        parse_mode="HTML",
        reply_markup=await get_action(show),
    )
