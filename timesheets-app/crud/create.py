from datetime import UTC, datetime
from bson import ObjectId
from bson.errors import InvalidId

from fastapi import HTTPException, status

import pymongo
from pymongo.errors import DuplicateKeyError
from database.db_conf import MongoDB
from utils.calculate import calc_valute


async def write_other(
    data: dict,
    user: int,
    valute_data: dict[str, float]
) -> bool | Exception:
    """
    Add a new income record (without updating the existing ones).

    :param valute_data:
    :param data: Recording data.
    :param user: ID user.
    :return: True on success, False on error.
    """
    type_operation: str = data.get("type_")
    required = {"amount", "description", "month", "year"}
    if not all(field in data for field in required):
        return False

    parse_date = datetime(data.get("year"), data.get("month"), 1)

    client = MongoDB()
    try:
        if type_operation == "income":
            collection = client.get_collection("other_income")
        else:
            collection = client.get_collection("expenses")

        record = {
            "user_id": user,
            "amount": float(data["amount"]),
            "description": data["description"],
            "month": int(data["month"]),
            "year": int(data["year"]),
            "valute": valute_data,
            "date": parse_date
        }

        result = collection.insert_one(record)
        return result.acknowledged

    except Exception as err:
        return err
    finally:
        client.close()


async def write_salary(
    data: dict,
    user_id: int,
    date: datetime,
    valute_data: dict[str, tuple[int, float]]
) -> None:
    """
    Save or update the user's settings.

    :param date:
    :param user_id:
    :param data:
    :param valute_data: Information about the ruble exchange rate.
    """
    client: MongoDB = MongoDB()
    period: int = 1 if date.day <= 15 else 2
    earned_in_valute = await calc_valute(data.get("earned"), valute_data)
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


async def delete_record(day_id: str) -> None:
    """
    Deleted the records from the database by user ID and date.

    :param day_id: The day's ID.
    """
    client: MongoDB = MongoDB()
    try:
        collection = client.get_collection("salaries")
        object_id = ObjectId(day_id)
        collection.delete_one({"_id": object_id})
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


async def remove_other_income_expense(collections: str, id_: str) -> None:
    """
    Delete the records from the database by record ID.

    :param collections: Type of collection (other income or expenses).
    :param id_: The ID of the record.
    """
    client: MongoDB = MongoDB()
    try:
        collection = client.get_collection(collections)
        collection.delete_one({
            "_id": id_
        })
    finally:
        client.close()
