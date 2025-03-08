from typing import Dict

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup
from aiogram.utils.markdown import hbold

from api.common import get_all_objects, get_full_info, delete_object_by_id
from config import PAGE_SIZE
from handlers.decorator_handler import decorator_errors
from keyboards.expenses import get_action
from keyboards.keyboards import confirmation, create_list_incomes_expenses
from states.expenses import ExpensesState
from utils.expenses import (
    get_expense_url,
    expense_url_by_id,
    generate_message_expense_info,
)

expense_router: Router = Router()


@expense_router.callback_query(F.data == "expenses_history")
@decorator_errors
async def expenses_get_history(
        callback: CallbackQuery, state: FSMContext
) -> None:
    """A handler for displaying the latest expenses."""
    data: dict[str, str | int] = await state.get_data()
    page: int = data.get("page", 1)
    url: str = await get_expense_url(page, page_size=PAGE_SIZE)

    result: dict = await get_all_objects(url, callback.from_user.id)

    await state.update_data(page=page, show=callback.data)
    keyword: InlineKeyboardMarkup = await create_list_incomes_expenses(
        result,
        "sh_expenses",
        "prev_exp",
        "next_exp"
    )

    await state.set_state(ExpensesState.show)
    text = "Ваши последние расходы."
    await callback.message.edit_text(
        text=hbold(text), reply_markup=keyword, parse_mode="HTML"
    )


@expense_router.callback_query(F.data.in_(["next_exp", "prev_exp"]))
@decorator_errors
async def next_prev_output_list_expenses(
    call: CallbackQuery, state: FSMContext
) -> None:
    """Show more expenses if any."""
    page: int = (await state.get_data()).get("page")

    if call.data == "next_exp":
        page += 1
    else:
        page -= 1

    url: str = await get_expense_url(page, page_size=PAGE_SIZE)
    result: Dict[str, list] = await get_all_objects(url, call.from_user.id)
    keyword: InlineKeyboardMarkup = await create_list_incomes_expenses(
        result,
        "sh_expenses",
        "prev_exp",
        "next_exp"
    )

    await state.set_state(ExpensesState.show)
    await state.update_data(page=page)
    await call.message.edit_reply_markup(reply_markup=keyword)


@expense_router.callback_query(ExpensesState.show, F.data.isdigit())
@decorator_errors
async def detail_incomes(call: CallbackQuery, state: FSMContext) -> None:
    """Show detailed expense information."""
    expense_id: int = int(call.data)
    show: str = (await state.get_data())["show"]
    url: str = await expense_url_by_id(expense_id)

    response: dict = await get_full_info(url, call.from_user.id)
    await state.update_data(expense_id=expense_id)
    text: str = await generate_message_expense_info(response)

    await state.set_state(ExpensesState.action)
    await call.message.edit_text(
        text=hbold(text),
        parse_mode="HTML",
        reply_markup=await get_action(show),
    )


@expense_router.callback_query(F.data == "remove_expense", ExpensesState.action)
async def remove_confirm(callback: CallbackQuery, state: FSMContext) -> None:
    """Confirmation of deletion."""
    await state.set_state(ExpensesState.remove)
    show: str = (await state.get_data())["show"]
    await callback.message.edit_text(
        text=hbold("Вы уверены?"),
        reply_markup=await confirmation(show),
        parse_mode="HTML",
    )


@expense_router.callback_query(ExpensesState.remove, F.data == "continue")
@decorator_errors
async def remove_expense_by_id(
        callback: CallbackQuery, state: FSMContext
) -> None:
    """
    The final income deletion handler.
    """
    data: dict[str, str | int] = await state.get_data()
    expense_id: int = data.get("expense_id")
    url: str = await expense_url_by_id(expense_id)
    await delete_object_by_id(url, callback.from_user.id)

    page: int = data.get("page", 1)
    url: str = await get_expense_url(page, page_size=PAGE_SIZE)
    result: dict = await get_all_objects(url, callback.from_user.id)

    await state.update_data(page=page)
    keyword: InlineKeyboardMarkup = await create_list_incomes_expenses(
        result,
        "sh_expenses",
        "prev_exp",
        "next_exp"
    )

    await state.set_state(ExpensesState.show)
    await callback.message.edit_text(
        text=hbold(f"Запись была удалена."),
        reply_markup=keyword,
        parse_mode="HTML",
    )
