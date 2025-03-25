import re
from datetime import datetime
from typing import Dict

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    Message,
    InlineKeyboardButton
)
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


@create_exp_router.callback_query(
    F.data.in_(["expense_add", "edit_expense_full"])
)
@decorator_errors
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
    keypad: InlineKeyboardMarkup = await create_calendar(
        year, month, "prev_cal_exp", "next_cal_exp"
    )

    await state.update_data(year=year, month=month)
    text = "Выберите дату расхода"
    await callback.message.edit_text(
        text=hbold(text), reply_markup=keypad, parse_mode="HTML"
    )


@create_exp_router.callback_query(
    F.data.in_(["next_cal_exp", "prev_cal_exp"])
)
@decorator_errors
async def next_and_prev_month(
    callback: CallbackQuery,
    state: FSMContext
) -> None:
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
@decorator_errors
async def create_expense_choice_account(
    callback: CallbackQuery, state: FSMContext
) -> None:
    """A handler for selecting an account to add/change expense to."""
    page: int = 1
    url: str = await account_url(page, PAGE_SIZE)
    type_: str = (await state.get_data())["type"]
    result: dict = await get_all_objects(url, callback.from_user.id)

    await state.update_data(page=page, date=callback.data)
    keypad: InlineKeyboardMarkup = await create_list_account(
        result, "prev_ce", "next_ce"
    )

    keypad.inline_keyboard.append([
        InlineKeyboardButton(
            text="🔙",
            callback_data=type_
        )
    ])
    await state.set_state(CreateExpenseState.account)
    await callback.message.edit_text(
        text=hbold("Выберите счет: "),
        reply_markup=keypad,
        parse_mode="HTML"
    )


@create_exp_router.callback_query(
        F.data.in_(["next_ce", "curr_ce",  "prev_ce"])
)
@decorator_errors
async def next_prev_account(call: CallbackQuery, state: FSMContext) -> None:
    """Show more accounts if any."""
    data = await state.get_data()
    page, type_ = data.get("page"), data.get("type")

    if call.data == "next_ce":
        page += 1

    elif call.data == "prev_ce":
        page -= 1

    url: str = await account_url(page, PAGE_SIZE)
    result: Dict[str, list] = await get_all_objects(url, call.from_user.id)
    keypad: InlineKeyboardMarkup = await create_list_account(
        result, "prev_ce", "next_ce"
    )

    keypad.inline_keyboard.append([
        InlineKeyboardButton(
            text="🔙",
            callback_data=type_
        )
    ])

    await state.set_state(CreateExpenseState.account)
    await state.update_data(page=page)
    await call.message.edit_text(
        text=hbold("Выберите счет:"),
        reply_markup=keypad,
        parse_mode="HTML"
    )


@create_exp_router.callback_query(CreateExpenseState.account, F.data.isdigit())
@decorator_errors
async def create_income_choice_category(
    callback: CallbackQuery, state: FSMContext
) -> None:
    """A handler for selecting an expense category to add an edit to."""
    page: int = 1

    await state.update_data(account_id=callback.data)
    await state.set_state(CreateExpenseState.expense_category)

    url: str = await get_expenses_category_url(page=page, page_size=PAGE_SIZE)
    result: dict = await get_all_objects(url, callback.from_user.id)
    keypad: InlineKeyboardMarkup = await create_list_category(
        result, "prev_cat_exp", "next_cat_exp"
    )

    keypad.inline_keyboard.append([
        InlineKeyboardButton(
            text="🔙",
            callback_data="curr_ce",

        )
    ])

    await callback.message.edit_text(
        text=hbold("Выберите категорию расхода: "),
        reply_markup=keypad,
        parse_mode="HTML",
    )


@create_exp_router.callback_query(
        F.data.in_(["next_cat_exp", "prev_cat_exp", "prev_curr_exc"])
)
@decorator_errors
async def next_prev_output_list_category(
    call: CallbackQuery, state: FSMContext
) -> None:
    """Show more category if any."""
    page: int = (await state.get_data()).get("page")

    if call.data == "next_cat_exp":
        page += 1

    elif call.data == "prev_cat_exp":
        page -= 1

    url: str = await get_expenses_category_url(page, PAGE_SIZE)
    result: Dict[str, list] = await get_all_objects(url, call.from_user.id)

    keypad: InlineKeyboardMarkup = await create_list_category(
        result, "prev_cat_exp", "next_cat_exp"
    )

    keypad.inline_keyboard.append([
        InlineKeyboardButton(
            text="🔙",
            callback_data="curr_ce",

        )
    ])

    await state.set_state(CreateExpenseState.expense_category)
    await state.update_data(page=page)
    await call.message.edit_text(
        text=hbold("Выберите категорию расхода: "),
        reply_markup=keypad,
        parse_mode="HTML"
    )


@create_exp_router.callback_query(
    CreateExpenseState.expense_category, F.data.isdigit()
)
@decorator_errors
async def create_expense_input_amount(
    callback: CallbackQuery,
    state: FSMContext
) -> None:
    """The handler for requesting the amount of expense from the user."""
    await state.update_data(expense_category=callback.data)
    type_: str = (await state.get_data()).get("type")

    if type_ == "expense_add":
        await state.set_state(CreateExpenseState.amount)
    else:
        await state.set_state(EditExpenseState.amount)

    await callback.message.edit_text(
        text=hbold("Введите сумму расхода: "),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Меню",
                    callback_data="main"
                ),
                InlineKeyboardButton(
                    text="🔙",
                    callback_data="prev_curr_exc"
                )
            ]
        ]),
        parse_mode="HTML"
    )


@create_exp_router.message(CreateExpenseState.amount)
@decorator_errors
async def ask_add_comment(message: Message, state: FSMContext) -> None:
    """
    A handler for saving the amount and entering a comment on the expense.
    """
    if not is_valid_balance(message.text):
        await message.answer(
            "Invalid balance format. Please enter a valid number.",
            reply_markup=cancel_
        )
        return
    await state.update_data(amount=message.text)
    await state.set_state(CreateExpenseState.comment)
    await message.answer(
        text=hbold("Введите комментарий. Если комментарий не нужен, "
                   "то, отправьте один любой символ."),
        reply_markup=cancel_,
        parse_mode="HTML"
    )


@create_exp_router.message(CreateExpenseState.comment)
@decorator_errors
async def create_expense_final(message: Message, state: FSMContext) -> None:
    """The final handler for the request to create a new expense."""
    data: dict[str, str | int] = await state.get_data()
    usr_id: int = message.from_user.id
    comment: str = message.text
    if comment in ["no comment", "no", "нет"] or len(comment) < 3:
        comment = ""

    dict_for_request: dict = await create_new_expenses_data(data, comment)
    response: dict[str, int | dict[str, int | str]] = await create_new_object(
        usr_id, expenses_url, dict_for_request
    )

    answer_message: str = await gen_answer_message_expense(response)
    await state.clear()
    await message.answer(
        text=hbold(answer_message),
        parse_mode="HTML",
        reply_markup=main_menu
    )
