from datetime import timedelta, date
from typing import Dict, Tuple


MONTH_DATA: Dict[int, str] = {
    1: "Январь",
    2: "Февраль",
    3: "Март",
    4: "Апрель",
    5: "Май",
    6: "Июнь",
    7: "Июль",
    8: "Август",
    9: "Сентябрь",
    10: "Октябрь",
    11: "Ноябрь",
    12: "Декабрь",
}

DAYS_LIST: tuple = ("Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс")


async def get_date(data: Dict[str, str], action: str) -> Tuple[int, int]:
    """
    The function gets the current transmitted date, and depending on the selected one
    actions either add or subtract a month.

    :param data: Dictionary with year and month.
    :param action: The selected action is prev next.
    :return: Год и месяц.
    """
    parse_date: date = date(int(data["year"]), int(data["month"]), 5)
    if action == "prev":
        find_date: date = parse_date - timedelta(days=30)
    else:
        find_date: date = parse_date + timedelta(days=30)
    return find_date.year, find_date.month
