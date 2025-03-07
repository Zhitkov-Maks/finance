import re
from datetime import datetime
from typing import Dict

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message
from aiogram.utils.markdown import hbold

from api.common import get_all_objects, create_new_object
from config import PAGE_SIZE, incomes_url
from handlers.decorator_handler import decorator_errors
from keyboards.accounts import create_list_account
from keyboards.category import create_list_category
from keyboards.create_calendar import create_calendar
from keyboards.keyboards import cancel_, main_menu
from states.incomes import CreateIncomes, EditIncomesState
from utils.accounts import account_url, is_valid_balance
from utils.common import date_pattern
from utils.create_calendar import get_date
from utils.incomes import (
    get_incomes_category_url,
    create_new_incomes_data,
    gen_answer_message,
)

create_inc_router: Router = Router()


@create_inc_router.callback_query(
    F.data.in_(["incomes_add", "edit_income_full"])
)
async def create_income_choice_date(
        callback: CallbackQuery, state: FSMContext
) -> None:
    """
    It is needed when creating and editing income.
    A handler for showing the user a calendar for selecting a date.
    """
    await state.update_data(type=callback.data)
    await state.set_state(CreateIncomes.date)

    year: int = datetime.now().year
    month: int = datetime.now().month
    keypad: InlineKeyboardMarkup = await create_calendar(
        year, month, "prev_cal_inc", "next_cal_inc"
    )

    await state.update_data(year=year, month=month)
    text = "Выберите дату дохода"

    await callback.message.edit_text(
        text=hbold(text),
        reply_markup=keypad,
        parse_mode="HTML",
    )


@create_inc_router.callback_query(
    F.data.in_(["next_cal_inc", "prev_cal_inc"])
)
@decorator_errors
async def next_and_prev_month(
        callback: CallbackQuery, state: FSMContext
) -> None:
    """
    Processes commands for the previous or next month.
    Generates calendars depending on the month.
    """
    data: Dict[str, str | int] = await state.get_data()
    action: str = "prev" if callback.data == "prev_cal_inc" else "next"
    year, month = await get_date(data, action)

    await state.update_data(year=year, month=month)
    await state.set_state(CreateIncomes.date)
    await callback.message.edit_reply_markup(
        reply_markup=await create_calendar(
            year, month, "prev_cal_inc", "next_cal_inc"
        )
    )


@create_inc_router.callback_query(
    CreateIncomes.date,
    lambda callback_query: re.match(date_pattern, callback_query.data),
)
async def create_income_choice_account(
    callback: CallbackQuery, state: FSMContext
) -> None:
    """A handler for selecting an account to add/change income to."""
    page: int = 1
    url: str = await account_url(page, PAGE_SIZE)

    result: dict = await get_all_objects(url, callback.from_user.id)

    await state.update_data(page=page, date=callback.data)
    keypad: InlineKeyboardMarkup = await create_list_account(
        result, "prev_ci", "next_ci"
    )

    await state.set_state(CreateIncomes.account)
    await callback.message.edit_text(
        text=hbold("Выберите счет: "),
        reply_markup=keypad,
        parse_mode="HTML",
    )


@create_inc_router.callback_query(F.data.in_(["next_ci", "prev_ci"]))
@decorator_errors
async def next_prev_output_list_incomes(
        call: CallbackQuery, state: FSMContext
) -> None:
    """Show more accounts if any."""
    page: int = (await state.get_data()).get("page")

    if call.data == "next_ci":
        page += 1
    else:
        page -= 1

    url: str = await account_url(page, PAGE_SIZE)
    result: Dict[str, list] = await get_all_objects(url, call.from_user.id)
    keypad: InlineKeyboardMarkup = await create_list_account(
        result, "prev_ci", "next_ci"
    )

    await state.set_state(CreateIncomes.account)
    await state.update_data(page=page)
    await call.message.edit_reply_markup(reply_markup=keypad)


@create_inc_router.callback_query(CreateIncomes.account, F.data.isdigit())
@decorator_errors
async def create_income_choice_category(
    callback: CallbackQuery, state: FSMContext
) -> None:
    """A handler for selecting an income category to add an edit to."""
    page: int = 1

    await state.update_data(account_id=callback.data)
    await state.set_state(CreateIncomes.income_category)

    url: str = await get_incomes_category_url(page=page, page_size=PAGE_SIZE)
    result: dict = await get_all_objects(url, callback.from_user.id)
    keypad: InlineKeyboardMarkup = await create_list_category(result)

    await callback.message.edit_text(
        text=hbold("Выберите категорию дохода: "),
        reply_markup=keypad,
        parse_mode="HTML",
    )


@create_inc_router.callback_query(F.data.in_(["next_cat_inc", "prev_cat_inc"]))
@decorator_errors
async def next_prev_output_list_category(
    call: CallbackQuery, state: FSMContext
) -> None:
    """Show more categories if any."""
    page: int = (await state.get_data()).get("page")

    if call.data == "next_cat_inc":
        page += 1
    else:
        page -= 1

    url: str = await get_incomes_category_url(page=page, page_size=PAGE_SIZE)
    result: Dict[str, list] = await get_all_objects(url, call.from_user.id)

    keyword: InlineKeyboardMarkup = await create_list_category(
        result, "prev_cat_inc", "next_cat_inc"
    )
    await state.set_state(CreateIncomes.income_category)
    await state.update_data(page=page)
    await call.message.edit_reply_markup(reply_markup=keyword)


@create_inc_router.callback_query(
    CreateIncomes.income_category, F.data.isdigit()
)
async def create_income_input_amount(
    callback: CallbackQuery, state: FSMContext
) -> None:
    """The handler for requesting the amount of income from the user."""
    await state.update_data(income_category=callback.data)
    type_: str = (await state.get_data()).get("type")

    if type_ == "incomes_add":
        await state.set_state(CreateIncomes.amount)
    else:
        await state.set_state(EditIncomesState.amount)

    await callback.message.edit_text(
        text=hbold("Введите сумму дохода: "),
        reply_markup=cancel_,
        parse_mode="HTML",
    )


@create_inc_router.message(CreateIncomes.amount)
async def ask_add_comment(message: Message, state: FSMContext) -> None:
    if not is_valid_balance(message.text):
        await message.answer(
            hbold("Неверный ввод. Нужно ввести целое число "
                  "или число через точку"),
            reply_markup=cancel_
        )
        return
    await state.update_data(amount=message.text)
    await state.set_state(CreateIncomes.comment)
    await message.answer(
        text=hbold("Введите комментарий. Если комментарий не нужен, "
                   "то, отправьте один любой символ."),
        reply_markup=cancel_,
        parse_mode="HTML"
    )


@create_inc_router.message(CreateIncomes.comment)
@decorator_errors
async def create_income_final(message: Message, state: FSMContext) -> None:
    """The final handler for the request to create a new income."""
    data: dict = await state.get_data()
    usr_id: int = message.from_user.id
    comment: str = message.text
    if comment in ["no comment", "no", "нет"] or len(comment) < 3:
        comment = ""

    dict_for_request: dict = await create_new_incomes_data(data, comment)
    response: dict = await create_new_object(
        usr_id, incomes_url, dict_for_request
    )
    answer_message: str = await gen_answer_message(response)

    await state.clear()
    await message.answer(
        text=hbold(answer_message),
        parse_mode="HTML",
        reply_markup=main_menu
    )
