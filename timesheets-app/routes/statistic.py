import asyncio

from fastapi import APIRouter, status, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from crud.statistics import aggregate_data, statistics_for_year
from database.db_conf import get_db
from schemas.statistics import StatisticForMonth, StatisticForYearSchema

statistic = APIRouter(prefix="/statistic", tags=["STATISTICS"])


@statistic.get(
    path="/year/", status_code=status.HTTP_200_OK, response_model=StatisticForYearSchema
)
async def get_statistics_for_year(
    user_id: int, year: int, db: AsyncIOMotorDatabase = Depends(get_db)
) -> dict:
    """Получить статистику за выбранный год."""
    return await statistics_for_year(year, user_id, db)


@statistic.get(
    path="/month/", status_code=status.HTTP_200_OK, response_model=StatisticForMonth
)
async def get_statistics_for_month(
    user_id: int, year: int, month: int, db: AsyncIOMotorDatabase = Depends(get_db)
) -> StatisticForMonth:
    """Получить статистику за выбранный год."""
    period_one, period_two, total = await asyncio.gather(
        aggregate_data(year, month, user_id, db, period=1),
        aggregate_data(year, month, user_id, db, period=2),
        aggregate_data(year, month, user_id, db),
    )
    return StatisticForMonth(period_one=period_one, period_two=period_two, total=total)
