import pymongo
from motor.motor_asyncio import AsyncIOMotorDatabase


async def add_many_shifts(shifts: list[dict], db: AsyncIOMotorDatabase) -> None:
    """
    Add a shift group to the database.

    :param db: Database.
    :param shifts: A dictionary list with data to be added to the database.
    """
    collection = db.get_collection("salaries")
    await collection.create_index(
        [("user_id", 1), ("date", 1)], unique=True, name="unique_user_date"
    )

    operations = []
    for shift in shifts:
        operations.append(
            pymongo.UpdateOne(
                {"user_id": shift["user_id"], "date": shift["date"]},
                {"$set": shift},
                upsert=True,
            )
        )

    if operations:
        await collection.bulk_write(operations, ordered=False)
