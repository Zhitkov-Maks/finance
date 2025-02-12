import asyncio

from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    Message,
)
from aiogram.utils.markdown import hbold

from api.common import get_full_info, edit_object
from handlers.decorator_handler import decorator_errors
from keyboards.accounts import choice_inline_edit, get_action_accounts
from keyboards.keyboards import cancel_
from loader import new_balance
from states.accounts import AccountsEditState, AccountsState
from utils.accounts import (
    generate_message_answer,
    is_valid_balance,
    account_by_id
)
from utils.common import remove_message_after_delay

edit_acc_router: Router = Router()


@edit_acc_router.callback_query(F.data == "edit")
async def choice_edit(callback: CallbackQuery):
    """A handler for selecting an account editing option."""
    await callback.message.edit_text(
        text=hbold("Выберите вариант редактирования."),
        reply_markup=choice_inline_edit,
        parse_mode="HTML"
    )


@edit_acc_router.callback_query(F.data == "edit_full")
async def full_edit(callback: CallbackQuery, state: FSMContext) -> None:
    """Handler for full account editing."""
    await state.set_state(AccountsEditState.name)
    answer: Message = await callback.message.edit_text(
        text=hbold("Введите новое имя счета: "),
        reply_markup=cancel_,
        parse_mode="HTML",
    )
    asyncio.create_task(remove_message_after_delay(60, answer))


@edit_acc_router.message(AccountsEditState.name)
async def input_new_name(message: Message, state: FSMContext) -> None:
    """Handler for new account name."""
    await state.update_data(name=message.text)
    await state.set_state(AccountsEditState.balance)
    answer: Message = await message.answer(
        text=hbold(new_balance), reply_markup=cancel_, parse_mode="HTML"
    )
    asyncio.create_task(remove_message_after_delay(60, [message, answer]))


@edit_acc_router.callback_query(F.data == "edit_balance")
async def change_only_balance(call: CallbackQuery, state: FSMContext) -> None:
    """The handler for requesting the balance."""
    await state.set_state(AccountsEditState.balance)
    await call.message.edit_text(
        text=hbold(new_balance),
        reply_markup=cancel_,
        parse_mode=ParseMode.MARKDOWN,
    )


@edit_acc_router.message(AccountsEditState.balance)
@decorator_errors
async def edited_account_balance(message: Message, state: FSMContext) -> None:
    """
    The handler sends a request to change the balance,
    and outputs new account information.
    """
    data: dict = await state.get_data()
    name: str | None = data.get("name", None)

    account_id, usr_id = data["account_id"], message.from_user.id
    url: str = await account_by_id(account_id)

    if not is_valid_balance(message.text):
        error_message: Message = await message.answer(
            "Неверный формат ввода, будьте внимательнее.", reply_markup=cancel_
        )
        asyncio.create_task(remove_message_after_delay(60, error_message))
        return

    method: str = "PUT"
    edit_data: dict = {"balance": message.text}
    if name is None:
        method = "PATCH"
    else:
        edit_data.update(name=name)
    await edit_object(url, usr_id, edit_data, method)

    response: dict = await get_full_info(url, usr_id)
    text: str = await generate_message_answer(response)

    await state.set_state(AccountsState.action)
    keyword: InlineKeyboardMarkup = await get_action_accounts(response.get("is_active"))

    await message.answer(text=hbold(text), parse_mode="HTML", reply_markup=keyword)
    asyncio.create_task(remove_message_after_delay(60, message))
