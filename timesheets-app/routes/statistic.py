from fastapi import APIRouter, status

from crud.statistics import aggregate_data, statistics_for_year
from schemas.statistics import AggregateSchema, StatisticForMonth, \
    StatisticForYearSchema

statistic = APIRouter(prefix="/statistic", tags=["STATISTICS"])


@statistic.get(
    path="/year/",
    status_code=status.HTTP_200_OK,
    response_model=StatisticForYearSchema
)
async def get_statistics_for_year(
    user_id: int,
    year: int
):
    """Получить статистику за выбранный год."""
    return await statistics_for_year(year, user_id)


@statistic.get(
    path="/month/",
    status_code=status.HTTP_200_OK,
    response_model=StatisticForMonth
)
async def get_statistics_for_month(
    user_id: int,
    year: int,
    month: int
):
    """Получить статистику за выбранный год."""
    period_one = await aggregate_data(year, month, user_id, period=1)
    period_two = await aggregate_data(year, month, user_id, period=2)
    total = await aggregate_data(year, month, user_id)
    return StatisticForMonth(
        period_one=period_one,
        period_two=period_two,
        total=total
    )
