from datetime import datetime
from dateutil.relativedelta import relativedelta
from fastapi import HTTPException
from starlette import status

from database.db_conf import MongoDB


async def get_information_for_month(
    user_id: int,
    year: int,
    month: int
) -> list:
    """
    Get the data for the selected month.

    :param user_id: The user's ID.
    :param year: The transmitted year.
    :param month: The transferred month.
    """
    client: MongoDB = MongoDB()
    try:
        collection = client.get_collection("salaries")
        start_date = datetime(year, month, 1)
        end_date = start_date + relativedelta(months=1)
        cursor = collection.find(
            {
                "user_id": user_id,
                "date": {"$gte": start_date, "$lt": end_date},
            }
        )
        results = cursor.to_list(length=None)
        return results
    finally:
        client.close()


async def get_info_by_date(user_id: int, date: str) -> dict:
    """
    Get the data for a specific selected date.

    :param user_id: The user's ID.
    :param date: A specific date to show to the user.
    """
    client: MongoDB = MongoDB()
    try:
        parse_date = datetime.strptime(date, "%Y-%m-%d")
        collection = client.get_collection("salaries")
        data: dict = collection.find_one(
            {"user_id": user_id, "date": parse_date}
        )
        return data or {}
    finally:
        client.close()


async def statistics_for_year(year: int, user_id: int) -> dict:
    """
    Aggregate the data for the year.

    :param user_id: The user's ID.
    :param year: The transmitted year.
    """
    client: MongoDB = MongoDB()
    try:
        collection = client.get_collection("salaries")
        start_date = datetime(year, 1, 1)
        end_date = datetime(year + 1, 1, 1)

        pipeline = [
            {
                "$match": {
                    "user_id": user_id,
                    "date": {"$gte": start_date, "$lt": end_date}
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
                    "som": {"$sum": "$valute.som"}
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
                    "som": {"$round": ["$som", 2]}
                }
            }
        ]

        result = collection.aggregate(pipeline).to_list()
        if len(result) != 0:
            return result[0]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "result": False,
                "description": "Нет данных за выбранный год."
            }
        )
    finally:
        client.close()


async def aggregate_data(
        year: int,
        month: int,
        user_id: int,
        period: int | None = None
) -> dict | None:
    """
    Calculate the amount of hours worked for the period
    and the amount of payment for the hours.

    :param user_id: The user's ID.
    :param year: The transmitted year.
    :param month: The transferred month.
    :param period: 1st or 2nd periods. If None - aggregates for entire month.
    """
    client: MongoDB = MongoDB()
    try:
        collection = client.get_collection("salaries")
        start_date = datetime(year, month, 1)
        end_date = start_date + relativedelta(months=1)

        # Базовый match
        match_stage = {
            "$match": {
                "user_id": user_id,
                "date": {"$gte": start_date, "$lt": end_date}
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
                    "som": {"$sum": "$valute.som"}
                }
            }
        ]

        result = collection.aggregate(pipeline).to_list()
        if len(result) != 0:
            return result[0]
        return None

    finally:
        client.close()
