from datetime import datetime, UTC

from fastapi import HTTPException
from starlette import status

from crud.many import add_many_shifts
from crud.settings import get_settings_user_by_id
from crud.get_data import get_hours_for_month, get_salary_for_day, update_salary
from crud.create import write_salary, delete_record
from crud.statistics import get_information_for_month
from utils.valute import get_valute_info
from utils.calculate import calc_valute


async def get_settings(user_id: int) -> tuple:
    """
    Return the basic user settings.

    :param user_id: The user's ID.
    """
    settings: dict = await get_settings_user_by_id(user_id)
    if not settings:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "result": False,
                "description": "Нет настроек для создания записи."
            }
        )

    price: float = float(settings.get("price_time", 0))
    cold: float = float(settings.get("price_cold", 0))
    overtime: float = float(settings.get("price_overtime", 0))
    award: float = float(settings.get("price_award", 0))
    return price, cold, overtime, award


async def calculation_overtime(
    settings: tuple,
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
    settings: tuple,
    time: float,
    user_id: int,
    date,
    total_hours=None
) -> dict:
    """
    Create a dictionary for future storage in the database.

    :param total_hours:
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
            user_id,
            year,
            month
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
    date: str
) -> None:
    """
    Generate the amount earned per shift.

    :param time: Hours worked.
    :param user_id: The user's ID.
    :param date: The date for recording.
    :return: The earned amount for the month.
    """
    valute_data: dict[str, tuple[int, float]] = await get_valute_info()
    settings: tuple[float] = await get_settings(user_id)
    parse_date = datetime.strptime(date, "%Y-%m-%d")
    salary = await earned_calculation(settings, time, user_id, parse_date)
    await write_salary(salary, user_id, parse_date, valute_data)
    await normalization_salary_for_month(
        user_id,
        settings,
        {"year": parse_date.year, "month": parse_date.month}
    )


async def critical_data(data: dict) -> tuple:
    old_need_data = {}
    if data.get("count_operations", 0) > 0:
        old_need_data.update(
            award_amount=data.get("award_amount"),
            count_operations=data.get("count_operations")
        )
    return (
        data.get("notes"),
        data.get("base_hours"),
        data.get("_id"),
        data.get("date"),
        old_need_data
    )


async def normalization_salary_for_month(
    user_id: int,
    settings: tuple,
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
        notes, time, day_id, date, old_data = await critical_data(item)
        await delete_record(day_id)
        salary = await recalculation_salary(
            time=time,
            user_id=user_id,
            date=date,
            valute_data=valute_data,
            settings=settings,
            total_hours=total_hours,
            old_data=old_data
        )
        total_hours += float(time)
        salaries.append(salary)

    await add_many_shifts(salaries)


async def recalculation_salary(
    time: float,
    user_id: int,
    date,  # datetime.date
    valute_data,
    settings: tuple,
    total_hours,
    old_data
) -> dict:
    """
    Recalculate the salary so that there are no errors in the calculations.

    :param valute_data:
    :param time: Hours worked.
    :param user_id: The user's ID.
    :param date: The date for recording.
    :param settings: User settings for the calculation.
    :param total_hours: The number of hours worked per month.
    :param old_data: If there is information about the premium.
    """
    salary = await earned_calculation(
        settings, time, user_id, date, total_hours
    )
    if old_data:
        salary.update(
            earned=(salary.get("earned") + old_data.get("award_amount"))
        )
    salary.update(
        user_id=user_id,
        date=date,
        period=1 if date.day <= 15 else 2,
        valute=await calc_valute(salary.get("earned"), valute_data),
        date_write=datetime.now(),
        **old_data
    )
    return salary


async def calc_in_currency(earned: float) -> dict:
    current_valute: dict = await get_valute_info()
    return await calc_valute(earned, current_valute)


async def earned_for_award(
    count_operations: int,
    user_id: int,
    day_id: str,
) -> dict:
    """
    Calculate the bonus and update the salary record.

    :param count_operations: The number of operations performed by the user.
    :param user_id: The user's ID.
    :param day_id: ID of the day.
    :return dict: Dictionary with shift data.
    """
    settings: dict = await get_settings_user_by_id(user_id)
    cost_award = settings.get("price_award")
    if cost_award is None:
        raise ValueError("Нет данных о стоимости операции!")

    earned_award: float = round(count_operations * float(cost_award), 2)
    current_day: dict = await get_salary_for_day(day_id)

    if current_day.get("award_amount"):
        earned = (
                current_day["earned"] -
                current_day["award_amount"] +
                earned_award
        )
    else:
        earned = earned_award + current_day["earned"]

    currency: dict = await calc_in_currency(earned)
    current_day.update(
        award_amount=earned_award,
        count_operations=count_operations,
        earned=earned,
        valute=currency
    )
    await update_salary(day_id, current_day)
    current_day.update(
        date=str(current_day.get("date")),
        day_id=str(current_day.get("_id"))
    )
    return current_day
