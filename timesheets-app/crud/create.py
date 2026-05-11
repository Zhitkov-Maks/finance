from datetime import UTC, datetime
from bson import ObjectId
from bson.errors import InvalidId

from fastapi import HTTPException, status

import pymongo
from pymongo.errors import DuplicateKeyError
from database.db_conf import MongoDB
from utils.calculate import calc_valute


async def write_salary(
    data: dict,
    user_id: int,
    date: datetime,
    valute_data: dict[str, tuple[int, float]]
) -> None:
    """
    Save or update the user's settings.

    :param date: The date of the completed shift.
    :param user_id: The user's ID.
    :param data: Shift data to save.
    :param valute_data: Information about the ruble exchange rate.
    """
    client: MongoDB = MongoDB()
    period: int = 1 if date.day <= 15 else 2
    earned_in_valute: dict[str, float] = await calc_valute(
        data.get("earned"), valute_data
    )
    data.update(
        period=period,
        valute=earned_in_valute,
        date_write=datetime.now(UTC)
    )
    collection = client.get_collection("salaries")

    collection.create_index(
        [("user_id", 1), ("date", 1)],
        unique=True,
        name="unique_user_date"
    )

    try:
        collection.update_one(
            {"user_id": user_id, "date": date},
            {"$set": data},
            upsert=True
        )
    except pymongo.errors.DuplicateKeyError:
        pass
    finally:
        client.close()


async def delete_record(day_id: str) -> dict:
    """
    Deleted the records from the database by user ID and date.

    :param day_id: The day's ID.
    """
    client: MongoDB = MongoDB()
    try:
        collection = client.get_collection("salaries")
        object_id = ObjectId(day_id)
        data = collection.find_one({"_id": object_id})
        collection.delete_one({"_id": object_id})
        return data
    except InvalidId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "result": False,
                "description": "Ошибка идентификатора."
            }
        )
    finally:
        client.close()
