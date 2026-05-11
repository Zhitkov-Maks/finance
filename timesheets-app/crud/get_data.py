from datetime import datetime

from bson.errors import InvalidId
from dateutil.relativedelta import relativedelta
from bson import ObjectId
from pymongo.errors import DuplicateKeyError

from database.db_conf import MongoDB


async def get_salary_for_day(day_id: str) -> dict | None:
    """
    Get the data for the day.

    :param day_id: The ID of the record.
    :return dict: A dictionary with detailed information per shift.
    """
    client = MongoDB()
    try:
        collection = client.get_collection("salaries")
        object_id = ObjectId(day_id)
        return collection.find_one({"_id": object_id})
    finally:
        client.close()


async def get_hours_for_month(
    user_id: int, year: int, month: int
) -> float:
    """
    Aggregate the hours for the month.

    :param month: The month for the request.
    :param year: The year for the request.
    :param user_id: The user's ID.
    """
    client: MongoDB = MongoDB()
    try:
        collection = client.get_collection("salaries")
        start_date = datetime(year, month, 1)
        end_date = start_date + relativedelta(months=1)
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
                    "total_hours": {"$sum": "$base_hours"}
                }
            },
            {
                "$project": {
                    "total_hours": {"$round": ["$total_hours", 1]}
                }
            }
        ]

        result = collection.aggregate(pipeline).to_list()
        if result and len(result) > 0:
            return result[0].get("total_hours", 0.0)
        return 0.0
    finally:
        client.close()


async def update_salary(day_id: str, data: dict) -> None:
    """
    Update your salary for the day.

    :param day_id: ID of the day.
    :param data: Dictionary with data to record.
    """
    client: MongoDB = MongoDB()
    collection = client.get_collection("salaries")
    try:
        object_id = ObjectId(day_id)
        collection.update_one(
            {"_id": object_id},
            {"$set": data},
            upsert=True
        )
    except (DuplicateKeyError, InvalidId):
        pass
    finally:
        client.close()
