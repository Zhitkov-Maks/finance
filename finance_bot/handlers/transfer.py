from typing import Dict, List

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message

from api.accounts import get_all_accounts
from api.transfer import create_transfer
from handlers.decorator_handler import decorator_errors
from keyboards.accounts import create_list_account
from keyboards.keyboards import cancel_, main_menu
from states.accounts import TransferStates
from utils.accounts import is_valid_balance

transfer = Router()


@transfer.callback_query(F.data == "transfer")
@decorator_errors
async def start_transfer(callback: CallbackQuery, state: FSMContext) -> None:
    """
    The handler for selecting the account to transfer.
    """
    page: int = 1
    account_id: int = (await state.get_data()).get("account_id")
    result: Dict[
        str, str | List[Dict[str, float | List[Dict[str, int | float | str]]]]
    ] = await get_all_accounts(callback.from_user.id, page=page)

    await state.update_data(page=page)
    keyword: InlineKeyboardMarkup = await create_list_account(
        result, int(account_id), transfer=True
    )
    await state.set_state(TransferStates.action)
    await callback.message.answer(
        text="Выберите счет куда перевести 💵",
        reply_markup=keyword,
    )


@transfer.callback_query(F.data.in_(["next_page", "prev_page"]))
@decorator_errors
async def next_prev_output_list_habits(call: CallbackQuery, state: FSMContext) -> None:
    """Show more invoices if any."""
    page: int = (await state.get_data()).get("page")
    account_id = (await state.get_data()).get("account_id")
    if call.data == "next_page":
        page += 1
    else:
        page -= 1

    result: Dict[
        str, str | List[Dict[str, float | List[Dict[str, int | float | str]]]]
    ] = await get_all_accounts(call.from_user.id, page=page)

    keyword: InlineKeyboardMarkup = await create_list_account(
        result, int(account_id), transfer=True
    )
    await state.update_data(page=page)
    await state.set_state(TransferStates.action)
    await call.message.edit_reply_markup(reply_markup=keyword)


@transfer.callback_query(TransferStates.action)
async def get_account_transfer_out(callback: CallbackQuery, state: FSMContext) -> None:
    """We save the account and request the balance."""
    await state.update_data(transfer_out=callback.data.split("_")[0])
    await state.update_data(account_out=callback.data.split("_")[1])
    await state.set_state(TransferStates.amount)
    await callback.message.answer(
        text="Введите сумму перевода 💰💰💰.", reply_markup=cancel_
    )


@transfer.message(TransferStates.amount)
async def get_amount_transfer(message: Message, state: FSMContext) -> None:
    """We are sending the data for the transfer."""
    data: dict = await state.get_data()
    transfer_in, transfer_out = data.get("account_id"), data.get("transfer_out")
    usr_id: int = message.from_user.id
    amount: str = message.text
    name, name_out = data.get("account"), data.get("account_out")

    if not is_valid_balance(message.text):
        await message.answer(
            "Invalid balance format. Please enter a valid number.", reply_markup=cancel_
        )
        return

    await create_transfer(transfer_in, transfer_out, usr_id, float(message.text))
    await state.clear()
    await message.answer(
        text=f"Перевод с {name} 👉🏻 {name_out} на сумму {amount}₽.",
        reply_markup=main_menu,
    )
