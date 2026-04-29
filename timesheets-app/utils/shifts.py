from datetime import datetime

from fastapi import HTTPException, status

from crud.many import add_many_shifts
from crud.statistics import get_information_for_month, get_info_by_date
from crud.get_data import get_salary_for_day
from utils.salary import get_settings, normalization_salary_for_month, \
    recalculation_salary
from utils.valute import get_valute_info


async def get_shifts_for_month(
    user_id: str,
    year: int,
    month: int
) -> list:
    returned_shifts = []
    shifts = await get_information_for_month(user_id, year, month)

    for shift in shifts:
        returned_shifts.append(
            {
                "day_id": str(shift.get("_id")),
                "base_hours": shift.get("base_hours"),
                "date": str(shift.get("date")),
                "earned": shift.get("earned")
            }
        )
    return returned_shifts


async def dictionary_formation(shift) -> dict:
    return {
        "day_id": str(shift.get("_id")),
        "base_hours": shift.get("base_hours"),
        "date": str(shift.get("date")),
        "earned": shift.get("earned"),
        "earned_cold": shift.get("earned_cold", 0),
        "earned_hours": shift.get("earned_hours"),
        "period": shift.get("period"),
        "valute": shift.get("valute")
    }


async def get_specific_shift(user_id, date: str) -> dict | bool:
    shift = await get_info_by_date(user_id, date)
    if shift:
        return await dictionary_formation(shift)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "result": False,
            "description": "Запись о смене не найдена."
        }
    )

async def get_specific_shift_by_day_id(day_id: str) -> dict | bool:
    shift = await get_salary_for_day(day_id)
    if shift:
        return await dictionary_formation(shift)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "result": False,
            "description": "Запись о смене не найдена."
        }
    )


async def create_data_by_add_shifts(
    user_id: str,
    time: float,
    list_dates: list[str]
) -> None:
    """
    Create shift records for the user based on the provided data.

    :param user_id: The user's ID.
    :param time: The total number of hours worked.
    :param list_dates: A list of string dates in the "YYYY-MM-DD"
                        format for which You need to create shift records.
    :return: None.
    """
    date_objects = [datetime.strptime(d, "%Y-%m-%d") for d in list_dates]
    data = {"year": date_objects[0].year, "month": date_objects[0].month}
    sorted_dates = sorted(date_objects)
    await save_shifts_all(user_id, time, sorted_dates, data)


async def save_shifts_all(
    user_id: str,
    time: float,
    sorted_dates: list,
    data: dict
) -> None:
    """
    Saves with a progress bar.

    :param data:
    :param user_id: The user's ID.
    :param time: The number of hours.
    :param sorted_dates: A sorted list of dates.
    """
    try:
        valute_data: dict[str, tuple[int, float]] = await get_valute_info()
        settings: tuple[float] = await get_settings(user_id)

        total_hours = 0
        salaries = []
        for i, d in enumerate(sorted_dates, 1):
            salary = await recalculation_salary(
                time=time,
                user_id=user_id,
                date=d,
                valute_data=valute_data,
                settings=settings,
                total_hours=total_hours
            )
            total_hours += float(time)
            salaries.append(salary)

        await add_many_shifts(salaries)
        await normalization_salary_for_month(user_id, settings, data)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "result": False,
                "description": "Ошибка при сохранении."
            }
        )
