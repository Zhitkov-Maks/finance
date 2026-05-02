from fastapi import APIRouter, status

from schemas.shifts import (
    ManyAddShifts, ShiftSchema,
    ListShiftSchema,
    SpecificShift
)
from schemas.general import SuccessSchema, NotFoundShift
from utils.salary import earned_for_award, earned_per_shift
from utils.shifts import (
    create_data_by_add_shifts, get_shifts_for_month,
    get_specific_shift,
    get_specific_shift_by_day_id
)
from crud.create import delete_record


shift_router = APIRouter(prefix="/shifts", tags=["SHIFTS"])


@shift_router.post(
    path="/",
    status_code=status.HTTP_201_CREATED,
    response_model=SuccessSchema
)
async def create_shift(
    user_id: int,
    data: ShiftSchema
) -> SuccessSchema:
    """Создать запись о рабочей смене."""
    data = data.model_dump()
    time, date = data.get("time"), data.get("date")
    await earned_per_shift(
        time,
        user_id,
        date
    )
    return SuccessSchema(result=True)


@shift_router.put(
    path="/",
    status_code=status.HTTP_201_CREATED,
    response_model=SuccessSchema
)
async def update_shift(user_id: int, data: ShiftSchema) -> SuccessSchema:
    """Изменить данные о рабочей смене."""
    data = data.model_dump()
    time, date, notes = data.get("time"), data.get("date"), data.get("notes")
    await earned_per_shift(
        time,
        user_id,
        date
    )
    return SuccessSchema(result=True)


@shift_router.get(
    path="/",
    status_code=status.HTTP_200_OK,
    response_model=ListShiftSchema
)
async def get_list_shifts_for_month(
    user_id: int,
    year: int,
    month: int
) -> ListShiftSchema:
    """Получить список смен за месяц, для добавления в календарь."""
    return ListShiftSchema(
        result=await get_shifts_for_month(user_id, year, month)
    )


@shift_router.get(
    path="/date/",
    status_code=status.HTTP_200_OK,
    response_model=SpecificShift,
    responses={404: {"model": NotFoundShift}}
)
async def get_shift_by_concrete_day(user_id: int, date: str):
    """Получить данные о смене по дате."""
    return await get_specific_shift(user_id, date)


@shift_router.get(
    path="/{day_id}/",
    status_code=status.HTTP_200_OK,
    response_model=SpecificShift
)
async def get_shift_by_day_id(day_id: str):
    """Получить данные о смене по идентификатору смены."""
    return await get_specific_shift_by_day_id(day_id)


@shift_router.post(
    path="/{day_id}/award/",
    status_code=status.HTTP_200_OK,
    response_model=SpecificShift
)
async def create_award_for_day(
    day_id: str,
    count_operations: int,
    user_id: int
):
    """Добавить данные о заработанной премии."""
    return await earned_for_award(count_operations, user_id, day_id)


@shift_router.delete(
    path="/{day_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_shift_by_day_id(day_id: str):
    """Удалить запись о смене по идентификатору."""
    await delete_record(day_id)


@shift_router.post(
    path="/{day_id}/many/",
    status_code=status.HTTP_201_CREATED,
    response_model=SuccessSchema
)
async def get_shift_by_day_id(
    user_id: int,
    data: ManyAddShifts
):
    """Групповое добавление смен за конкретный месяц."""
    data = data.model_dump()
    time = data.get("hours")
    list_dates = data.get("dates")
    await create_data_by_add_shifts(user_id, time, list_dates)
    return SuccessSchema(result=True)
