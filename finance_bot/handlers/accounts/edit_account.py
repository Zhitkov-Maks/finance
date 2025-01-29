from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    Message,
)

from api.accounts import edit_account, get_full_info
from handlers.decorator_handler import decorator_errors
from keyboards.accounts import choice_inline_edit, get_action_accounts
from keyboards.keyboards import cancel_
from loader import new_balance
from states.accounts import AccountsEditState, AccountsState
from utils.accounts import generate_message_answer, is_valid_balance

edit = Router()


@edit.callback_query(F.data == "edit")
async def choice_edit(callback: CallbackQuery):
    """Show a list of accounts."""
    await callback.message.answer(
        text="Выберите вариант редактирования.", reply_markup=choice_inline_edit
    )


@edit.callback_query(F.data == "edit_full")
async def full_edit(callback: CallbackQuery, state: FSMContext) -> None:
    """Handler for full account editing."""
    await state.set_state(AccountsEditState.name)
    await callback.message.answer(
        text="Введите новое имя счета: ",
        reply_markup=cancel_,
    )


@edit.message(AccountsEditState.name)
async def input_new_name(message: Message, state: FSMContext) -> None:
    """Handler for new account name."""
    await state.update_data(name=message.text)
    await state.set_state(AccountsEditState.balance)
    await message.answer(text=new_balance, reply_markup=cancel_)


@edit.callback_query(F.data == "edit_balance")
async def change_only_balance(call: CallbackQuery, state: FSMContext) -> None:
    """The handler for requesting the balance."""
    await state.set_state(AccountsEditState.balance)
    await call.message.answer(text=new_balance, reply_markup=cancel_)


@edit.message(AccountsEditState.balance)
@decorator_errors
async def edited_account_balance(message: Message, state: FSMContext) -> None:
    """
    The handler sends a request to change the balance,
    and outputs new account information.
    """
    data: dict = await state.get_data()
    name: str | None = data.get("name", None)

    account_id, usr_id = data["account_id"], message.from_user.id

    if not is_valid_balance(message.text):
        await message.answer(
            "Invalid balance format. Please enter a valid number.", reply_markup=cancel_
        )
        return

    edit_data: dict = {"name": name, "balance": message.text}
    await edit_account(account_id, usr_id, edit_data)

    response = await get_full_info(account_id, usr_id)
    text: str = await generate_message_answer(response)

    await state.set_state(AccountsState.action)
    keyword: InlineKeyboardMarkup = await get_action_accounts()

    await message.answer(text=text, parse_mode="HTML", reply_markup=keyword)
