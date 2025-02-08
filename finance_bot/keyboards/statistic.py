from typing import List

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils.create_calendar import MONTH_DATA


async def get_month(year: int, month: int, data: str) -> InlineKeyboardMarkup:
    """
    A keyboard so that statistics can be scrolled by month.
    :param operation: Incomes or expenses
    :param year: Transferred year.
    :param month: Transferred month.
    :return: A keyboard for statistics.
    """
    if data == 'statistic_exp':
        operation = "statistic_expenses"
    else:
        operation = "statistic_incomes"

    buttons: List[List[InlineKeyboardButton]] = [
        [
            InlineKeyboardButton(
                text=f"{MONTH_DATA[month]} {year}г",
                callback_data=f"{operation}")
        ],
        [
            InlineKeyboardButton(
                text="<<",
                callback_data=f"prev_month"
            ),
            InlineKeyboardButton(
                text="меню",
                callback_data=f"main"
            ),
            InlineKeyboardButton(
                text=">>",
                callback_data=f"next_month"
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
