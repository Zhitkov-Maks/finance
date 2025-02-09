import asyncio
import os
from datetime import datetime
from typing import Dict

from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile
from aiogram.utils.markdown import hbold

from api.common import get_full_info
from config import statistic_url, accounts_url
from handlers.decorator_handler import decorator_errors
from keyboards.keyboards import main_menu
from keyboards.statistic import get_month
from utils.create_calendar import get_date, MONTH_DATA
from utils.statistic import (
    gen_message_statistics,
    get_statistic_current_month,
    get_url_and_type_message,
    get_message_incomes_by_expenses,
)

statistic_route: Router = Router()


@statistic_route.callback_query(F.data.in_(["statistic_expenses", "statistic_incomes"]))
@decorator_errors
async def get_expenses_for_month(call: CallbackQuery, state: FSMContext) -> None:
    """A handler for displaying the amount of income or expense."""
    month: int = datetime.now().month
    year: int = datetime.now().year
    url: str = statistic_url[call.data].format(month=month, year=year)

    amount: float = await get_statistic_current_month(url, call.from_user.id)
    answer, sign = (
        ("расходы", "-") if call.data == "statistic_expenses" else ("доходы", "+")
    )
    await call.answer(
        text=f"{MONTH_DATA[month]}, {answer}: {sign}{amount}₽.", show_alert=True
    )


@statistic_route.callback_query(F.data == "accounts_data")
@decorator_errors
async def get_expenses_for_month(call: CallbackQuery, state: FSMContext) -> None:
    """Handler for displaying the balance of all accounts."""
    url: str = accounts_url + "?page=1&page_size=1"
    amount: float = await get_statistic_current_month(url, call.from_user.id, True)
    answer: str = f"На ваших счетах {amount}₽"
    await call.answer(answer, show_alert=True)


@statistic_route.callback_query(F.data == "expenses_by_incomes")
@decorator_errors
async def incomes_to_expenses(call: CallbackQuery, state: FSMContext) -> None:
    """A handler for showing the ratio of income to expenses."""
    month, year = datetime.now().month, datetime.now().year

    # Запускаем оба запроса одновременно
    amount_expenses, amount_incomes = await asyncio.gather(
        get_statistic_current_month(
            statistic_url["statistic_expenses"].format(month=month, year=year),
            call.from_user.id,
        ),
        get_statistic_current_month(
            statistic_url["statistic_incomes"].format(month=month, year=year),
            call.from_user.id,
        ),
    )
    filename: str = await get_message_incomes_by_expenses(
        amount_incomes, amount_expenses, call.from_user.id, year, month
    )
    await call.message.answer_photo(FSInputFile(filename), reply_markup=main_menu)
    os.remove(filename)


@statistic_route.callback_query(F.data.in_(["statistic_exp", "statistic_inc"]))
@decorator_errors
async def get_statistic_for_month(callback: CallbackQuery, state: FSMContext) -> None:
    """
    A handler for displaying statistics for the month
    by category in descending order of the amount.
    """
    month, year = datetime.now().month, datetime.now().year
    await state.update_data(month=month, year=year, type_=callback.data)

    url, text = await get_url_and_type_message(callback.data, year, month)
    result: dict = await get_full_info(url, callback.from_user.id)
    message: str = await gen_message_statistics(result)

    await callback.message.answer(
        text=hbold(text + f"\n{message}"),
        parse_mode="HTML",
        reply_markup=await get_month(year, month, callback.data),
    )


@statistic_route.callback_query(F.data.in_(["next_month", "prev_month"]))
@decorator_errors
async def next_and_prev_month(callback: CallbackQuery, state: FSMContext) -> None:
    """A handler for displaying statistics for the next or previous month."""
    data: Dict[str, str | int] = await state.get_data()
    action: str = "prev" if callback.data == "prev_month" else "next"
    type_operation: str = data.get("type_")
    year, month = await get_date(data, action)
    await state.update_data(year=year, month=month)

    url, text = await get_url_and_type_message(type_operation, year, month)
    result: dict = await get_full_info(url, callback.from_user.id)
    message: str = await gen_message_statistics(result)

    keyboard_markup = await get_month(year, month, type_operation)

    try:
        await callback.message.edit_text(
            text=hbold(text + f"\n{message}"),
            parse_mode="HTML",
            reply_markup=keyboard_markup,
        )
        await callback.answer()
        return

    except TelegramBadRequest:
        await callback.message.answer(
            text=hbold(text + f"\n{message}"),
            parse_mode="HTML",
            reply_markup=keyboard_markup,
        )
