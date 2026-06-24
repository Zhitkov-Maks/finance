from datetime import datetime
from dateutil.relativedelta import relativedelta
from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from starlette import status


async def get_information_for_month(
    user_id: int, year: int, month: int, db: AsyncIOMotorDatabase
) -> list:
    """
    Get the data for the selected month.

    :param db: Database.
    :param user_id: The user's ID.
    :param year: The transmitted year.
    :param month: The transferred month.
    """
    collection = db.get_collection("salaries")
    start_date = datetime(year, month, 1)
    end_date = start_date + relativedelta(months=1)
    cursor = collection.find(
        {
            "user_id": user_id,
            "date": {"$gte": start_date, "$lt": end_date},
        }
    )
    results = await cursor.to_list(length=None)
    return results


async def get_info_by_date(user_id: int, date: str, db: AsyncIOMotorDatabase) -> dict:
    """
    Get the data for a specific selected date.

    :param db: Database.
    :param user_id: The user's ID.
    :param date: A specific date to show to the user.
    """
    parse_date = datetime.strptime(date, "%Y-%m-%d")
    collection = db.get_collection("salaries")
    data: dict = await collection.find_one({"user_id": user_id, "date": parse_date})
    return data or {}


async def statistics_for_year(
    year: int, user_id: int, db: AsyncIOMotorDatabase
) -> dict:
    """
    Aggregate the data for the year.

    :param db: Database.
    :param user_id: The user's ID.
    :param year: The transmitted year.
    """
    collection = db.get_collection("salaries")
    start_date = datetime(year, 1, 1)
    end_date = datetime(year + 1, 1, 1)

    pipeline = [
        {
            "$match": {
                "user_id": user_id,
                "date": {"$gte": start_date, "$lt": end_date},
            }
        },
        {
            "$group": {
                "_id": None,
                "total_hours": {"$sum": "$base_hours"},
                "total_earned": {"$sum": "$earned"},
                "total_award": {"$sum": "$award_amount"},
                "dollar": {"$sum": "$valute.dollar"},
                "euro": {"$sum": "$valute.euro"},
                "yena": {"$sum": "$valute.yena"},
                "som": {"$sum": "$valute.som"},
            }
        },
        {
            "$project": {
                "total_hours": {"$round": ["$total_hours", 2]},
                "total_earned": {"$round": ["$total_earned", 2]},
                "total_award": {"$round": ["$total_award", 2]},
                "dollar": {"$round": ["$dollar", 2]},
                "euro": {"$round": ["$euro", 2]},
                "yena": {"$round": ["$yena", 2]},
                "som": {"$round": ["$som", 2]},
            }
        },
    ]

    result = await collection.aggregate(pipeline).to_list()
    if len(result) != 0:
        return result[0]
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail={"result": False, "description": "Нет данных за выбранный год."},
    )


async def aggregate_data(
    year: int,
    month: int,
    user_id: int,
    db: AsyncIOMotorDatabase,
    period: int | None = None,
) -> dict | None:
    """
    Calculate the amount of hours worked for the period
    and the amount of payment for the hours.

    :param db: Database.
    :param user_id: The user's ID.
    :param year: The transmitted year.
    :param month: The transferred month.
    :param period: 1st or 2nd periods. If None - aggregates for entire month.
    """
    collection = db.get_collection("salaries")
    start_date = datetime(year, month, 1)
    end_date = start_date + relativedelta(months=1)

    # Базовый match
    match_stage = {
        "$match": {
            "user_id": user_id,
            "date": {"$gte": start_date, "$lt": end_date},
        }
    }

    # Добавляем фильтр по period только если он указан
    if period is not None:
        match_stage["$match"]["period"] = period

    pipeline = [
        match_stage,
        {
            "$group": {
                "_id": None,
                "total_base_hours": {"$sum": "$base_hours"},
                "total_earned": {"$sum": "$earned"},
                "total_earned_hours": {"$sum": "$earned_hours"},
                "total_earned_cold": {"$sum": "$earned_cold"},
                "total_award": {"$sum": "$award_amount"},
                "total_operations": {"$sum": "$count_operations"},
                "total_overtime": {"$sum": "$earned_overtime"},
                "total_hours_overtime": {"$sum": "$hours_overtime"},
                "dollar": {"$sum": "$valute.dollar"},
                "euro": {"$sum": "$valute.euro"},
                "yena": {"$sum": "$valute.yena"},
                "som": {"$sum": "$valute.som"},
            }
        },
    ]

    result = await collection.aggregate(pipeline).to_list()
    if len(result) != 0:
        return result[0]
    return None
