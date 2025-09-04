from typing import Dict

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup
from aiogram.utils.markdown import hbold

from api.common import get_all_objects, get_full_info, delete_object_by_id
from config import PAGE_SIZE
from handlers.decorator_handler import decorator_errors
from keyboards.transaction import get_action
from keyboards.keyboards import confirmation, create_list_incomes_expenses
from states.transaction import TransactionState
from utils.transaction import generate_message_transaction_info
from utils.transaction import choice_url_transaction

transaction_show_router: Router = Router()


@transaction_show_router.callback_query(
    F.data.in_(["expenses_history", "incomes_history"])
)
@decorator_errors
async def expenses_get_history(
        callback: CallbackQuery, state: FSMContext
) -> None:
    """A handler for displaying the latest expenses."""
    data: dict[str, str | int] = await state.get_data()
    page: int = data.get("page", 1)

    url: str = choice_url_transaction(callback.data)
    full_url: str = url + f"?page={page}&page_size={PAGE_SIZE}"
    result: dict = await get_all_objects(full_url, callback.from_user.id)

    await state.update_data(page=page, show=callback.data)
    keyword: InlineKeyboardMarkup = await create_list_incomes_expenses(
        result,
        "sh_expenses" if callback.data.startswith("exp") else "sh_incomes",
        "prev_transaction",
        "next_transaction"
    )
    await state.set_state(TransactionState.show)
    text = "Расходы" if callback.data.startswith("exp") else "Доходы"
    await callback.message.edit_text(
        text=hbold(text), reply_markup=keyword, parse_mode="HTML"
    )


@transaction_show_router.callback_query(
    F.data.in_(["next_transaction", "prev_transaction"])
)
@decorator_errors
async def next_prev_output_list_expenses(
    call: CallbackQuery, state: FSMContext
) -> None:
    """Show more expenses if any."""
    data: dict = await state.get_data()
    page, type_tr = data.get("page"), data.get("show")

    if call.data == "next_transaction":
        page += 1
    else:
        page -= 1

    url: str = choice_url_transaction(type_tr)
    full_url: str = url + f"?page={page}&page_size={PAGE_SIZE}"
    result: Dict[str, list] = await get_all_objects(
        full_url, call.from_user.id
    )
    keyword: InlineKeyboardMarkup = await create_list_incomes_expenses(
        result,
        "sh_expenses" if type_tr.startswith("exp") else "sh_incomes",
        "prev_transaction",
        "next_transaction"
    )

    await state.set_state(TransactionState.show)
    await state.update_data(page=page)
    await call.message.edit_reply_markup(reply_markup=keyword)


@transaction_show_router.callback_query(TransactionState.show, F.data.isdigit())
@decorator_errors
async def detail_incomes(call: CallbackQuery, state: FSMContext) -> None:
    """Show detailed expense information."""
    transaction_id: int = int(call.data)
    show: str = (await state.get_data())["show"]

    url: str = choice_url_transaction(show)
    full_url = url + f"{transaction_id}/"
    response: dict = await get_full_info(full_url, call.from_user.id)
    await state.update_data(transaction_id=transaction_id)
    text: str = await generate_message_transaction_info(response)

    await state.set_state(TransactionState.action)
    await call.message.edit_text(
        text=hbold(text),
        parse_mode="HTML",
        reply_markup=await get_action(show),
    )


@transaction_show_router.callback_query(
        F.data == "remove_transaction",
        TransactionState.action
)
@decorator_errors
async def remove_confirm(callback: CallbackQuery, state: FSMContext) -> None:
    """Confirmation of deletion."""
    await state.set_state(TransactionState.remove)
    show: str = (await state.get_data())["show"]
    await callback.message.edit_text(
        text=hbold("Вы уверены?"),
        reply_markup=await confirmation(show),
        parse_mode="HTML",
    )


@transaction_show_router.callback_query(
    TransactionState.remove, F.data == "continue"
)
@decorator_errors
async def remove_expense_by_id(
        callback: CallbackQuery, state: FSMContext
) -> None:
    """
    The final income deletion handler.
    """
    data: dict[str, str | int] = await state.get_data()
    show: str = data.get("show")
    transaction_id: int = data.get("transaction_id")
    url: str = choice_url_transaction(show)
    delete_url = url + f"{transaction_id}/"
    await delete_object_by_id(delete_url, callback.from_user.id)

    page: int = data.get("page", 1)
    full_url: str = url + f"?page={page}&page_size={PAGE_SIZE}"
    result: dict = await get_all_objects(full_url, callback.from_user.id)

    await state.update_data(page=page)
    keyword: InlineKeyboardMarkup = await create_list_incomes_expenses(
        result,
        "sh_expenses" if callback.data.startswith("exp") else "sh_incomes",
        "prev_transaction",
        "next_transaction"
    )

    await state.set_state(TransactionState.show)
    await callback.message.edit_text(
        text=hbold("Запись была удалена."),
        reply_markup=keyword,
        parse_mode="HTML",
    )
