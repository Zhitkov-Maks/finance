from typing import Dict, List

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup

from api.accounts import (
    get_all_accounts,
    get_full_info,
    delete_account_by_id,
    change_toggle_active,
)
from handlers.decorator_handler import decorator_errors
from keyboards.accounts import create_list_account, get_action_accounts
from keyboards.keyboards import confirm_menu, main_menu
from states.accounts import AccountsState
from utils.accounts import generate_message_answer, update_account_state

account = Router()


@account.callback_query(F.data == "accounts")
@decorator_errors
async def start_account(callback: CallbackQuery, state: FSMContext):
    """Show a list of accounts."""
    data = await state.get_data()
    page: int = data.get("page", 1)
    result: Dict[
        str, str | List[Dict[str, float | List[Dict[str, int | float | str]]]]
    ] = await get_all_accounts(callback.from_user.id, page=page)

    await state.update_data(page=page)
    total_balance: float = result.get("results")[0].get("total_balance", 0)
    keyword: InlineKeyboardMarkup = await create_list_account(result)

    await state.set_state(AccountsState.show)
    await callback.message.answer(
        text=f"Баланс на ваших счетах составляет {total_balance:_}₽",
        reply_markup=keyword,
    )


@account.callback_query(F.data == "next_page")
@decorator_errors
async def next_output_list_habits(call: CallbackQuery, state: FSMContext) -> None:
    """Show more invoices if any."""
    page: int = (await state.get_data()).get("page")

    result: Dict[
        str, str | List[Dict[str, float | List[Dict[str, int | float | str]]]]
    ] = await get_all_accounts(call.from_user.id, page=page + 1)

    keyword: InlineKeyboardMarkup = await create_list_account(result)
    await state.update_data(page=page + 1)
    await state.set_state(AccountsState.show)
    await call.message.edit_reply_markup(reply_markup=keyword)


@account.callback_query(F.data == "prev_page")
@decorator_errors
async def prev_output_list_habits(call: CallbackQuery, state: FSMContext) -> None:
    """Show the previous page."""
    page: int = (await state.get_data()).get("page")

    result: Dict[
        str, str | List[Dict[str, float | List[Dict[str, int | float | str]]]]
    ] = await get_all_accounts(call.from_user.id, page=page - 1)
    keyword: InlineKeyboardMarkup = await create_list_account(result)
    await state.update_data(page=page - 1)
    await state.set_state(AccountsState.show)
    await call.message.edit_reply_markup(reply_markup=keyword)


@account.callback_query(F.data == "change-toggle")
async def change_toggle(callback: CallbackQuery, state: FSMContext) -> None:
    """Toggle the active status of an account."""
    data = await state.get_data()
    account_id = data.get("account_id")
    current_active = data.get("is_active", False)

    # Toggle the activity status
    new_active_status = not current_active
    await change_toggle_active(account_id, callback.from_user.id, new_active_status)

    # Fetch updated account info
    response = await get_full_info(int(account_id), callback.from_user.id)
    await update_account_state(state, response)

    # Update reply markup based on new active status
    keyword = await get_action_accounts(response.get("is_active"))
    await callback.message.edit_reply_markup(reply_markup=keyword)


@account.callback_query(AccountsState.show, F.data.isdigit())
@decorator_errors
async def detail_account(call: CallbackQuery, state: FSMContext) -> None:
    """Show detailed account information."""
    account_id = int(call.data)

    # Fetch account info
    response = await get_full_info(account_id, call.from_user.id)
    await update_account_state(state, response)

    # Generate and send the response text
    text = await generate_message_answer(response)
    await call.message.answer(
        text=text,
        parse_mode="HTML",
        reply_markup=await get_action_accounts(response.get("is_active")),
    )


@account.callback_query(F.data == "remove", AccountsState.action)
async def remove_confirm(callback: CallbackQuery, state: FSMContext) -> None:
    """Confirmation of deletion."""
    await state.set_state(AccountsState.remove)
    await callback.message.answer(text="Вы уверены?", reply_markup=confirm_menu)


@account.callback_query(AccountsState.remove, F.data == "continue")
@decorator_errors
async def remove_account_by_id(callback: CallbackQuery, state: FSMContext) -> None:
    """
    The final account deletion handler.
    """
    data: dict = await state.get_data()
    await delete_account_by_id(data["account_id"], callback.from_user.id)
    await state.clear()
    await callback.message.answer(
        text=f"Счет <{data['account']}> был удален!", reply_markup=main_menu
    )
