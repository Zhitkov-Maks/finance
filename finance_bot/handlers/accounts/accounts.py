from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup
from aiogram.utils.markdown import hbold

from api.accounts import change_toggle_active
from api.common import get_all_objects, get_full_info, delete_object_by_id
from config import PAGE_SIZE
from handlers.decorator_handler import decorator_errors
from keyboards.accounts import create_list_account, get_action_accounts
from keyboards.keyboards import main_menu, confirmation
from states.accounts import AccountsState
from utils.accounts import (
    generate_message_answer,
    update_account_state,
    account_url,
    account_by_id,
)

account: Router = Router()


@account.callback_query(F.data == "accounts")
@decorator_errors
async def start_account(callback: CallbackQuery, state: FSMContext) -> None:
    """Show a list of accounts."""
    data: dict = await state.get_data()
    page: int = data.get("page", 1)
    url: str = await account_url(page, PAGE_SIZE)

    result: dict = await get_all_objects(url, callback.from_user.id)

    await state.update_data(page=page)
    total_balance: float = result.get("results")[0].get("total_balance", 0)
    keyword: InlineKeyboardMarkup = await create_list_account(result)

    await state.set_state(AccountsState.show)
    text: str = f"Баланс {total_balance:_}₽"
    await callback.message.edit_text(
        text=hbold(text),
        reply_markup=keyword,
        parse_mode="HTML",
    )


@account.callback_query(F.data == "next_acc")
@decorator_errors
async def next_output_list_habits(
        call: CallbackQuery, state: FSMContext
) -> None:
    """Show more invoices if any."""
    page: int = (await state.get_data()).get("page")
    url: str = await account_url(page + 1, PAGE_SIZE)

    result: dict = await get_all_objects(url, call.from_user.id)

    keyword: InlineKeyboardMarkup = await create_list_account(result)
    await state.update_data(page=page + 1)
    await state.set_state(AccountsState.show)
    await call.message.edit_reply_markup(reply_markup=keyword)


@account.callback_query(F.data == "prev_acc")
@decorator_errors
async def prev_output_list_habits(
        call: CallbackQuery, state: FSMContext
) -> None:
    """Show the previous page."""
    page: int = (await state.get_data()).get("page")
    url: str = await account_url(page - 1, PAGE_SIZE)

    result: dict = await get_all_objects(url, call.from_user.id)

    keyword: InlineKeyboardMarkup = await create_list_account(result)
    await state.update_data(page=page - 1)
    await state.set_state(AccountsState.show)
    await call.message.edit_reply_markup(reply_markup=keyword)


@account.callback_query(F.data == "change-toggle")
@decorator_errors
async def change_toggle(callback: CallbackQuery, state: FSMContext) -> None:
    """Toggle the active status of an account."""
    data: dict = await state.get_data()
    account_id: int = data.get("account_id")
    current_active: bool = data.get("is_active", False)
    url: str = await account_by_id(account_id)

    # Toggle the activity status
    new_active_status: bool = not current_active
    await change_toggle_active(
        account_id, callback.from_user.id, new_active_status
    )

    # Fetch updated account info
    response: dict = await get_full_info(url, callback.from_user.id)
    await update_account_state(state, response)

    # Update reply markup based on new active status
    text: str = await generate_message_answer(response)
    keyword: InlineKeyboardMarkup = await get_action_accounts(
        response.get("is_active")
    )
    await callback.message.edit_text(
        text=hbold(text),
        reply_markup=keyword,
        parse_mode="HTML",
    )


@account.callback_query(AccountsState.show, F.data.isdigit())
@decorator_errors
async def detail_account(call: CallbackQuery, state: FSMContext) -> None:
    """Show detailed account information."""
    account_id: int = int(call.data)
    url: str = await account_by_id(account_id)

    # Fetch account info
    response: dict = await get_full_info(url, call.from_user.id)
    await update_account_state(state, response)

    # Generate and send the response text
    text: str = await generate_message_answer(response)
    await state.set_state(AccountsState.action)
    await call.message.edit_text(
        text=hbold(text),
        parse_mode="HTML",
        reply_markup=await get_action_accounts(response.get("is_active")),
    )


@account.callback_query(F.data == "remove", AccountsState.action)
@decorator_errors
async def remove_confirm(callback: CallbackQuery, state: FSMContext) -> None:
    """Confirmation of deletion."""
    await state.set_state(AccountsState.remove)
    await callback.message.edit_text(
        text=hbold("Вы уверены?"),
        reply_markup=await confirmation("accounts"),
        parse_mode="HTML"
    )


@account.callback_query(AccountsState.remove, F.data == "continue")
@decorator_errors
async def remove_account_by_id(
        callback: CallbackQuery, state: FSMContext
) -> None:
    """The final account deletion handler."""
    data: dict = await state.get_data()
    account_id: int = data.get("account_id")
    url: str = await account_by_id(account_id)

    await delete_object_by_id(url, callback.from_user.id)
    await state.clear()
    await callback.message.edit_text(
        text=hbold(f"Счет <{data['account']}> был удален!"),
        reply_markup=main_menu,
        parse_mode="HTML"
    )
