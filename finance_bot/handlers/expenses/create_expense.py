import re
from datetime import datetime
from typing import Dict, List

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message
from aiogram.utils.markdown import hbold

from api.common import get_all_objects, create_new_object
from config import PAGE_SIZE, expenses_url
from handlers.decorator_handler import decorator_errors
from keyboards.accounts import create_list_account
from keyboards.category import create_list_category
from keyboards.create_calendar import create_calendar
from keyboards.keyboards import cancel_, main_menu
from states.expenses import CreateExpenseState, EditExpenseState
from utils.accounts import account_url, is_valid_balance
from utils.common import date_pattern
from utils.create_calendar import get_date
from utils.expenses import (
    get_expenses_category_url,
    create_new_expenses_data,
    gen_answer_message_expense,
)

create_exp_router: Router = Router()


@create_exp_router.callback_query(F.data.in_(["expense_add", "edit_expense_full"]))
async def create_expense_choice_date(
    callback: CallbackQuery, state: FSMContext
) -> None:
    """
    It is needed when creating and editing expense.
    A handler for showing the user a calendar for selecting a date.
    """
    await state.update_data(type=callback.data)
    await state.set_state(CreateExpenseState.date)

    year: int = datetime.now().year
    month: int = datetime.now().month
    keyboard: InlineKeyboardMarkup = await create_calendar(
        year, month, "prev_cal_exp", "next_cal_exp"
    )

    await state.update_data(year=year, month=month)
    await callback.message.answer(text="Выберите дату расхода", reply_markup=keyboard)


@create_exp_router.callback_query(F.data.in_(["next_cal_exp", "prev_cal_exp"]))
@decorator_errors
async def next_and_prev_month(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Processes commands for the previous or next month.
    Generates calendars depending on the month.
    """
    data: Dict[str, str | int] = await state.get_data()
    action: str = "prev" if callback.data == "prev_cal_exp" else "next"
    year, month = await get_date(data, action)

    await state.update_data(year=year, month=month)
    await state.set_state(CreateExpenseState.date)
    await callback.message.edit_reply_markup(
        reply_markup=await create_calendar(
            year, month, "prev_cal_exp", "next_cal_exp"
        )
    )


@create_exp_router.callback_query(
    CreateExpenseState.date,
    lambda callback_query: re.match(date_pattern, callback_query.data),
)
async def create_expense_choice_account(
    callback: CallbackQuery, state: FSMContext
) -> None:
    """A handler for selecting an account to add/change expense to."""
    data: dict[str, str | int] = await state.get_data()
    page: int = data.get("page", 1)
    url: str = await account_url(page, PAGE_SIZE)

    result: Dict[
        str, str | List[Dict[str, float | List[Dict[str, int | float | str]]]]
    ] = await get_all_objects(url, callback.from_user.id)

    await state.update_data(page=page, date=callback.data)
    keyword: InlineKeyboardMarkup = await create_list_account(
        result, "prev_ce", "next_ce"
    )

    await state.set_state(CreateExpenseState.account)
    await callback.message.answer(
        text="Выберите счет: ",
        reply_markup=keyword,
    )


@create_exp_router.callback_query(F.data.in_(["next_ce", "prev_ce"]))
@decorator_errors
async def next_prev_account(call: CallbackQuery, state: FSMContext) -> None:
    """Show more accounts if any."""
    page: int = (await state.get_data()).get("page")

    if call.data == "next_ce":
        page += 1
    else:
        page -= 1

    url: str = await account_url(page, PAGE_SIZE)
    result: Dict[str, list] = await get_all_objects(url, call.from_user.id)
    keyword: InlineKeyboardMarkup = await create_list_account(
        result, "prev_ce", "next_ce"
    )

    await state.set_state(CreateExpenseState.account)
    await state.update_data(page=page)
    await call.message.edit_reply_markup(reply_markup=keyword)


@create_exp_router.callback_query(CreateExpenseState.account, F.data.isdigit())
@decorator_errors
async def create_income_choice_category(
    callback: CallbackQuery, state: FSMContext
) -> None:
    """A handler for selecting an expense category to add an edit to."""
    data: dict[str, str | int] = await state.get_data()
    page: int = data.get("page", 1)

    await state.update_data(account_id=callback.data)
    await state.set_state(CreateExpenseState.expense_category)

    url: str = await get_expenses_category_url(page=page, page_size=PAGE_SIZE)
    result: dict[str, int | list[dict[str, int | str]]] = await get_all_objects(
        url, callback.from_user.id
    )
    keyboard: InlineKeyboardMarkup = await create_list_category(
        result, "prev_cat_exp", "next_cat_exp"
    )
    await callback.message.answer(
        text="Выберите категорию расхода: ", reply_markup=keyboard
    )


@create_exp_router.callback_query(F.data.in_(["next_cat_exp", "prev_cat_exp"]))
@decorator_errors
async def next_prev_output_list_category(
    call: CallbackQuery, state: FSMContext
) -> None:
    """Show more category if any."""
    page: int = (await state.get_data()).get("page")

    if call.data == "next_cat_exp":
        page += 1
    else:
        page -= 1

    url: str = await get_expenses_category_url(page, PAGE_SIZE)
    result: Dict[str, list] = await get_all_objects(url, call.from_user.id)

    keyword: InlineKeyboardMarkup = await create_list_category(
        result, "prev_cat_exp", "next_cat_exp"
    )

    await state.set_state(CreateExpenseState.account)
    await state.update_data(page=page)
    await call.message.edit_reply_markup(reply_markup=keyword)


@create_exp_router.callback_query(CreateExpenseState.expense_category, F.data.isdigit())
async def create_expense_input_amount(
    callback: CallbackQuery, state: FSMContext
) -> None:
    """The handler for requesting the amount of expense from the user."""
    await state.update_data(expense_category=callback.data)
    type_: str = (await state.get_data()).get("type")

    if type_ == "expense_add":
        await state.set_state(CreateExpenseState.amount)
    else:
        await state.set_state(EditExpenseState.amount)

    await callback.message.answer(text="Введите сумму расхода: ", reply_markup=cancel_)


@create_exp_router.message(CreateExpenseState.amount)
@decorator_errors
async def create_expense_final(message: Message, state: FSMContext) -> None:
    """The final handler for the request to create a new expense."""
    data: dict[str, str | int] = await state.get_data()
    usr_id: int = message.from_user.id

    if not is_valid_balance(message.text):
        await message.answer(
            "Invalid balance format. Please enter a valid number.", reply_markup=cancel_
        )
        return

    dict_for_request: dict[str, str | float | int] = await create_new_expenses_data(
        data, float(message.text)
    )
    response: dict[str, int | dict[str, int | str]] = await create_new_object(
        usr_id, expenses_url, dict_for_request
    )
    answer_message: str = await gen_answer_message_expense(response)
    await message.answer(
        text=hbold(answer_message), parse_mode="HTML", reply_markup=main_menu
    )
