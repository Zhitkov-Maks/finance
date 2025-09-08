import re
from datetime import datetime
from typing import Dict

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from aiogram.utils.markdown import hbold

from config import PAGE_SIZE
from api.common import create_new_object, get_all_objects
from handlers.decorator_handler import decorator_errors
from utils.transaction import (
    choice_type_transaction,
    get_category_url,
    create_transaction_data,
    choice_url_transaction,
    gen_answer_message_transaction
)
from states.transaction import CreateTransactionState, EditTransactionState
from keyboards.create_calendar import create_calendar
from utils.create_calendar import get_date
from utils.common import date_pattern
from keyboards.accounts import create_list_account
from keyboards.category import create_list_category
from keyboards.keyboards import cancel_, main_menu
from utils.accounts import account_url, is_valid_balance


transaction_router: Router = Router()
transaction_type: list[str] = [
    "expense_add",
    "edit_transaction_full",
    "incomes_add"
]


@transaction_router.callback_query(
    F.data.in_(transaction_type)
)
@decorator_errors
async def create_expense_choice_date(
    callback: CallbackQuery, state: FSMContext
) -> None:
    """
    It is needed when creating and editing expense.
    A handler for showing the user a calendar for selecting a date.
    """
    call_data: str = callback.data
    if "exp" in call_data or "inc" in call_data:
        type_transaction = call_data
    else:
        # Then we take the data from what was opened. 
        # History of expenses or income.
        type_transaction: str = (await state.get_data())["show"]

    await state.update_data(type=type_transaction)
    await state.set_state(CreateTransactionState.date)

    year: int = datetime.now().year
    month: int = datetime.now().month
    keypad: InlineKeyboardMarkup = await create_calendar(year, month)

    await state.update_data(year=year, month=month)
    text = choice_type_transaction(callback.data)
    await callback.message.edit_text(
        text=hbold(text), reply_markup=keypad, parse_mode="HTML"
    )


@transaction_router.callback_query(
    F.data.in_(["next_cal_tr", "prev_cal_tr"])
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
    action: str = "prev" if callback.data == "prev_cal_tr" else "next"
    year, month = await get_date(data, action)

    await state.update_data(year=year, month=month)
    await state.set_state(CreateTransactionState.date)
    await callback.message.edit_reply_markup(
        reply_markup=await create_calendar(
            year, month, "prev_cal_tr", "next_cal_tr"
        )
    )


@transaction_router.callback_query(
    CreateTransactionState.date,
    lambda callback_query: re.match(date_pattern, callback_query.data),
)
@decorator_errors
async def create_expense_choice_account(
    callback: CallbackQuery, state: FSMContext
) -> None:
    """A handler for selecting an account to add/change expense to."""
    page: int = 1
    date: str = callback.data
    url: str = await account_url(page, PAGE_SIZE)
    type_: str = (await state.get_data())["type"]
    result: dict = await get_all_objects(url, callback.from_user.id)

    await state.update_data(page=page, date=date)
    keypad: InlineKeyboardMarkup = await create_list_account(
        result, "prev_acc_tr", "next_acc_tr"
    )

    keypad.inline_keyboard.append([
        InlineKeyboardButton(
            text="🔙",
            callback_data=type_
        )
    ])
    await state.set_state(CreateTransactionState.account)
    await callback.message.edit_text(
        text=hbold(f"Дата: {date}\nВыберите счет: "),
        reply_markup=keypad,
        parse_mode="HTML"
    )


@transaction_router.callback_query(
        F.data.in_(["next_acc_tr", "curr_acc_tr",  "prev_acc_tr"])
)
@decorator_errors
async def next_prev_account(call: CallbackQuery, state: FSMContext) -> None:
    """Show more accounts if any."""
    data = await state.get_data()
    page, type_, date = data.get("page"), data.get("type"), data.get("date")

    if call.data == "next_acc_tr":
        page += 1

    elif call.data == "prev_acc_tr":
        page -= 1

    url: str = await account_url(page, PAGE_SIZE)
    result: Dict[str, list] = await get_all_objects(url, call.from_user.id)
    keypad: InlineKeyboardMarkup = await create_list_account(
        result, "prev_acc_tr", "next_acc_tr"
    )

    keypad.inline_keyboard.append([
        InlineKeyboardButton(
            text="🔙",
            callback_data=type_
        )
    ])

    await state.set_state(CreateTransactionState.account)
    await state.update_data(page=page)
    await call.message.edit_text(
        text=hbold(f"Дата: {date}\nВыберите счет: "),
        reply_markup=keypad,
        parse_mode="HTML"
    )


@transaction_router.callback_query(
    CreateTransactionState.account, F.data.split("_")[0].isdigit()
)
@decorator_errors
async def create_income_choice_category(
    callback: CallbackQuery, state: FSMContext
) -> None:
    """A handler for selecting an expense category to add an edit to."""
    page: int = 1
    account_name = callback.data.split("_")[1]
    await state.update_data(
        account_id=callback.data.split("_")[0],
        account_name=account_name
    )
    await state.set_state(CreateTransactionState.category)
    type_transaction = (await state.get_data())["type"]
    url: str = await get_category_url(
        type_transaction, page=page, page_size=PAGE_SIZE
    )
    result: dict = await get_all_objects(url, callback.from_user.id)
    keypad: InlineKeyboardMarkup = await create_list_category(
        result, "prev_cat_tr", "next_cat_tr"
    )

    keypad.inline_keyboard.append([
        InlineKeyboardButton(
            text="🔙",
            callback_data="curr_acc_tr",
        )
    ])
    await callback.message.edit_text(
        text=hbold(
            f"Счет: {account_name};"
            f"\nВыберите категорию транзакции: "
        ),
        reply_markup=keypad,
        parse_mode="HTML",
    )


@transaction_router.callback_query(
        F.data.in_(["next_cat_tr", "prev_cat_tr", "prev_curr_tr"])
)
@decorator_errors
async def next_prev_output_list_category(
    call: CallbackQuery, state: FSMContext
) -> None:
    """Show more category if any."""
    data = await state.get_data()
    page, account_name = data.get("page"), data.get("account_name")

    if call.data == "next_cat_tr":
        page += 1

    elif call.data == "prev_cat_tr":
        page -= 1

    type_transaction = data["type"]
    url: str = await get_category_url(
        type_transaction, page=page, page_size=PAGE_SIZE
    )
    result: Dict[str, list] = await get_all_objects(url, call.from_user.id)

    keypad: InlineKeyboardMarkup = await create_list_category(
        result, "prev_cat_tr", "next_cat_tr"
    )

    keypad.inline_keyboard.append([
        InlineKeyboardButton(
            text="🔙",
            callback_data="curr_acc_tr",
        )
    ])

    await state.set_state(CreateTransactionState.category)
    await state.update_data(page=page)
    await call.message.edit_text(
        text=hbold(
            f"Счет: {account_name};"
            f"\nВыберите категорию транзакции: "
        ),
        reply_markup=keypad,
        parse_mode="HTML",
    )


@transaction_router.callback_query(
    CreateTransactionState.category, F.data.split("_")[0].isdigit()
)
@decorator_errors
async def create_expense_input_amount(
    callback: CallbackQuery,
    state: FSMContext
) -> None:
    """The handler for requesting the amount of expense from the user."""
    await state.update_data(category=callback.data.split("_")[0])
    type_: str = (await state.get_data()).get("type")

    if type_ in ["expense_add", "incomes_add"]:
        await state.set_state(CreateTransactionState.amount)
    else:
        await state.set_state(EditTransactionState.amount)

    await callback.message.edit_text(
        text=hbold(
            f"Категория: {callback.data.split("_")[1]};\n"
            f"Введите сумму транзакции: "
        ),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Меню",
                    callback_data="main"
                ),
                InlineKeyboardButton(
                    text="🔙",
                    callback_data="prev_curr_tr"
                )
            ]
        ]),
        parse_mode="HTML"
    )


@transaction_router.message(CreateTransactionState.amount)
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
    await state.set_state(CreateTransactionState.comment)
    await message.answer(
        text=hbold("Введите комментарий. Если комментарий не нужен, "
                   "то, отправьте один любой символ."),
        reply_markup=cancel_,
        parse_mode="HTML"
    )


@transaction_router.message(CreateTransactionState.comment)
@decorator_errors
async def create_expense_final(message: Message, state: FSMContext) -> None:
    """The final handler for the request to create a new expense."""
    data: dict[str, str | int] = await state.get_data()
    type_transaction = data["type"]
    usr_id: int = message.from_user.id
    comment: str = message.text
    if comment in ["no comment", "no", "нет"] or len(comment) < 3:
        comment = ""

    dict_for_request: dict = await create_transaction_data(data, comment)
    url: str = choice_url_transaction(type_transaction)
    response: dict[str, int | dict[str, int | str]] = await create_new_object(
        usr_id, url, dict_for_request
    )

    answer_message: str = await gen_answer_message_transaction(
        type_transaction, response
    )
    await state.clear()
    await message.answer(
        text=hbold(answer_message),
        parse_mode="HTML",
        reply_markup=main_menu
    )
