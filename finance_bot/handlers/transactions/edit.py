from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.markdown import hbold

from api.common import edit_object, get_full_info
from config import BASE_URL
from handlers.decorator_handler import decorator_errors
from keyboards.transaction import get_action, choice_edit
from keyboards.transaction import cancel_action
from states.transaction import TransactionState, EditTransactionState
from utils.accounts import is_valid_balance
from utils.transaction import (
    create_new_data,
    generate_message_transaction_info
)

edit_transaction: Router = Router()


@edit_transaction.callback_query(F.data == "edit_transaction")
@decorator_errors
async def edit_expense_choice(
        callback: CallbackQuery, state: FSMContext
) -> None:
    """A handler for selecting an expense editing option."""
    data: dict = await state.get_data()
    expense_id = data.get("transaction_id")
    await state.set_state(TransactionState.show)
    await state.update_data(transaction=callback.data)
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


@edit_transaction.callback_query(F.data == "edit_transaction_balance")
@decorator_errors
async def edit_balance(callback: CallbackQuery, state: FSMContext) -> None:
    """
    The handler for requesting the amount of expense when editing only
    the balance.
    """
    await state.set_state(EditTransactionState.comment)
    await state.update_data(method="PATCH")
    await callback.message.edit_text(
        text=hbold("Введите новую сумму транзакции."),
        reply_markup=await cancel_action(),
        parse_mode="HTML",
    )


@edit_transaction.message(EditTransactionState.amount)
@decorator_errors
async def ask_add_comment(message: Message, state: FSMContext) -> None:
    """Handler for the amount and input of the expense comment."""
    if not is_valid_balance(message.text):
        await message.answer(
            "Ошибка ввода, попробуйте еще раз.",
            reply_markup=await cancel_action()
        )
        return

    await state.update_data(amount=message.text)
    await state.set_state(EditTransactionState.comment)
    await message.answer(
        text=hbold("Введите комментарий. Если комментарий не нужен, "
                   "то, отправьте один любой символ."),
        reply_markup=await cancel_action(),
        parse_mode="HTML"
    )


@edit_transaction.message(EditTransactionState.comment)
@decorator_errors
async def edit_expense_request(message: Message, state: FSMContext) -> None:
    """The final handler for editing."""
    data: dict[str, str | int] = await state.get_data()
    transaction_id, usr_id = data["transaction_id"], message.from_user.id
    show: str = data["show"]
    url = BASE_URL + f"transaction/{transaction_id}/"
    method: str = ""

    if data.get("method"):
        method = data.pop("method")
        if not is_valid_balance(message.text):
            await message.answer(
                "Invalid balance format. Please enter a valid number.",
                reply_markup=await cancel_action()
            )
            return
        edit_data: dict = {"amount": float(message.text)}

    else:
        comment: str = message.text
        if comment in ["no comment", "no", "нет"] or len(comment) < 3:
            comment = ""
        edit_data: dict = await create_new_data(data, comment)

    await edit_object(url, usr_id, edit_data, method)
    response: dict = await get_full_info(url, usr_id)

    text: str = await generate_message_transaction_info(response)
    await state.set_state(TransactionState.action)
    await message.answer(
        text=hbold(text),
        parse_mode="HTML",
        reply_markup=await get_action(show),
    )
