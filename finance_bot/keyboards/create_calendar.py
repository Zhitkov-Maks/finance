from calendar import monthrange
from datetime import date, datetime
from typing import List, Tuple

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils.create_calendar import DAYS_LIST, MONTH_DATA


async def create_list_with_calendar_days(
        day_week: int,
        days_in_month: int,
        days: int
) -> List[str]:
    """
    The function generates a list with calendar days plus empty
    cells before the first number, plus empty cells after the
    last day of the month.

    :param day_week: The number of the day of the week is \
                        the first of the month.
    :param days_in_month: There are only days in a month.
    :param days: The size of the calendar field.
    :return List: A list with a calendar field.
    """
    return (
            [" "] * day_week
            + [f"{i:02}" for i in range(1, days_in_month + 1)]
            + [" "] * (days - days_in_month - day_week)
            )


async def generate_base_calendar(
    field_size: int,
    numbers_list: List[str],
    month_keyword: list,
    year: int,
    month: int
) -> None:
    """
    The function of generating the main part of the calendar.
    Fills the calendar with buttons.

    :param field_size: The size of the calendar field.
    :param numbers_list: The calendar field.
    :param month_keyword: The keyboard itself is in the form of a calendar.
    :param year: It is needed for forming the date.
    :param month: It is needed for forming the date.
    :return List: The inline keyboard.
    """
    current_date: str = str(datetime.now().date())
    for i in range(7):
        row: List[InlineKeyboardButton] = [
            InlineKeyboardButton(text=DAYS_LIST[i], callback_data=DAYS_LIST[i])
        ]
        day: int = i

        for _ in range(field_size):
            create_date: str = f"{year}-{month:02}-{numbers_list[day]}"

            if numbers_list[day] == " ":
                text = " "

            elif create_date == current_date:
                text = f"[ {numbers_list[day]} ]"

            else:
                text = f"{numbers_list[day]} ˑ"

            row.append(
                InlineKeyboardButton(text=text, callback_data=create_date)
            )
            day += 7

        month_keyword.append(row)


async def create_calendar(
    year: int,
    month: int,
    prev: str = "prev_cal_tr",
    next_d: str = "next_cal_tr"
) -> InlineKeyboardMarkup:
    """
    Генерирует календарь за указанный месяц.
    :param next_d: The name for the button that will show the
                    next month when clicked.
    :param prev: The name for the button that will display
                    the previous month when clicked.
    :param year: The year to display in the calendar.
    :param month: The month to display in the calendar.

    :return: Online keyboard with the days of the month.
    """
    day_week: int = date(year, month, 1).weekday()
    days_in_month: int = monthrange(year, month)[1]

    month_keyword: List[List[InlineKeyboardButton]] = []
    field_size, days = await get_month_range(day_week, days_in_month)

    numbers_list: List[str] = await create_list_with_calendar_days(
        day_week, days_in_month, days
    )

    month_keyword.append(
        [
            InlineKeyboardButton(text=f"{MONTH_DATA[month]} {year}г",
                                 callback_data="calendar")]
    )

    await generate_base_calendar(
        field_size, numbers_list, month_keyword, year, month
    )

    month_keyword.append(
        [
            InlineKeyboardButton(text="<<", callback_data=prev),
            InlineKeyboardButton(text="Меню", callback_data="main"),
            InlineKeyboardButton(text=">>", callback_data=next_d),
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=month_keyword)


async def get_month_range(
        day_week: int, days_in_month: int
) -> Tuple[int, int]:
    """
    Defines the size of the field and the number of days to display in
    the calendar based on the day of the week and the number of
    days in the month.

    :param day_week: An integer representing the day of
                        the week (0 is Monday, 6 is Sunday).
    :param days_in_month: The total number of days in a month.

    :return: A tuple of two integers:
             - field_size: The size of the field to display (4, 5, or 6).
             - days: The total number of days to display (28, 35, or 42).
    """
    field_size: int = 5
    days: int = 35

    if day_week + days_in_month > 35:
        field_size = 6
        days = 42

    elif days_in_month + day_week < 29:
        field_size = 4
        days = 28

    return field_size, days
