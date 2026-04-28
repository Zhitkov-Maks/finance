from datetime import datetime, UTC

from crud.many import add_many_shifts
from crud.settings import get_settings_user_by_id
from crud.get_data import get_hours_for_month
from crud.create import write_salary, delete_record
from crud.statistics import get_information_for_month
from utils.valute import get_valute_info
from utils.calculate import calc_valute


async def get_settings(user_id: str) -> tuple[float]:
    """
    Return the basic user settings.

    :param user_id: The user's ID.
    """
    settings: dict = await get_settings_user_by_id(user_id)
    if not settings:
        raise KeyError("Нет настроек для рассчета.")

    price: float = float(settings.get("price_time", 0))
    cold: float = float(settings.get("price_cold", 0))
    overtime: float = float(settings.get("price_overtime", 0))
    award: float = float(settings.get("price_award", 0))
    return price, cold, overtime, award


async def calculation_overtime(
    settings: tuple[float],
    time: float,
    norm: int,
    total_hours: float
) -> tuple:
    """
    Calculate how much the user earned per shift
    if he has already overworked by the hour.

    :param settings: User settings.
    :param time: Time worked.
    :param norm: The standard of hours per month.
    :param total_hours: How many hours have been worked already this month.
    :return dict: A tuple with data to save.
    """
    price, _, overtime, _ = settings
    time_over = (time + total_hours) - norm
    earned = round(
        min(time_over, time) * (price + overtime) +
        max((time - time_over), 0) * price, 2
    )
    return earned, min(time_over, time), overtime * min(time_over, time)


async def earned_calculation(
    settings: tuple[float],
    time: float,
    user_id: int,
    date,
    total_hours=None
) -> dict[str, float]:
    """
    Create a dictionary for future storage in the database.

    :param settings: User settings.
    :param time: Time worked.
    :param user_id: User's ID.
    :param date: The date for adding the shift.
    :return dict: Dictionary with the configuration for writing.
    """
    configuration: dict[str, float] = dict()
    year, month = date.year, date.month
    if total_hours is None:
        total_hours: tuple[float] = await get_hours_for_month(
            user_id, year, month
        )
    norm_hours = 180 if month == 2 else 190

    earned_time = time * settings[0]
    earned_cold = time * settings[1]
    configuration.update(
        base_hours=time,
        earned_cold=earned_cold,
        earned=(earned_time + earned_cold),
        earned_hours=earned_time
    )

    if settings[2] > 0 and (time + total_hours) > norm_hours:
        (
            earned_time,
            hours_overtime,
            earned_overtime
        ) = await calculation_overtime(settings, time, norm_hours, total_hours)

        configuration.update(
            hours_overtime=hours_overtime,
            earned_overtime=earned_overtime,
            earned=(earned_time + earned_cold),
            earned_hours=earned_time - earned_overtime,
        )
    return configuration


async def earned_per_shift(
    time: float,
    user_id: int,
    date: str,
    notes: str | None,
    data: dict
) -> tuple[float, float]:
    """
    Generate the amount earned per shift..

    :param time: Hours worked.
    :param user_id: The user's ID.
    :return: The earned amount for the month.
    :param date: The date for recording.
    """
    valute_data: dict[str, tuple[int, float]] = await get_valute_info()
    settings: tuple[float] = await get_settings(user_id)
    parse_date = datetime.strptime(date, "%Y-%m-%d")
    salary = await earned_calculation(settings, time, user_id, parse_date)

    if notes:
        salary.update(notes=notes)

    await write_salary(salary, user_id, parse_date, valute_data)
    await normalization_salary_for_month(user_id, settings, data)


async def normalization_salary_for_month(
    user_id: int,
    settings: dict,
    data: dict
) -> None:
    """
    Recalculation of monthly salary as the hours may be
    changed and the calculation may be incorrect.

    :param user_id: The user's ID.
    :param settings: User settings.
    :param data: User settings.
    """
    year = data.get("year", datetime.now(UTC).year)
    month = data.get("month", datetime.now(UTC).month)
    result = await get_information_for_month(user_id, year, month)
    sorted_result = sorted(result, key=lambda x: x["date"])
    valute_data: dict[str, tuple[int, float]] = await get_valute_info()

    total_hours = 0
    salaries: list[dict] = []

    for item in sorted_result:
        notes = item.get("notes")
        time = item.get("base_hours")
        date = item.get("date")
        await delete_record(datetime.strftime(date, "%Y-%m-%d"), user_id)
        salary = await recalculation_salary(
            time=time,
            user_id=user_id,
            date=date,
            notes=notes,
            valute_data=valute_data,
            settings=settings,
            total_hours=total_hours
        )
        total_hours += float(time)
        salaries.append(salary)

    await add_many_shifts(salaries)


async def recalculation_salary(
    time: float,
    user_id: int,
    date: str,
    notes: str | None,
    valute_data,
    settings: tuple,
    total_hours
) -> tuple[float, float]:
    """
    Recalculate the salary so that there are no errors in the calculations.

    :param time: Hours worked.
    :param user_id: The user's ID.
    :param date: The date for recording.
    :param notes: Note if it exists.
    :param settings: User settings for the calculation.
    :param total_hours: The number of hours worked per month.
    """
    salary = await earned_calculation(
        settings, time, user_id, date, total_hours
    )
    salary.update(
        user_id=user_id,
        date=date,
        period=1 if date.day <= 15 else 2,
        valute=await calc_valute(salary.get("earned"), valute_data),
        date_write=datetime.now()
    )

    if notes:
        salary.update(notes=notes)
    return salary
