from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from starlette import status


async def create_settings(data: dict, user_id: int, db: AsyncIOMotorDatabase) -> None:
    """
    Create or update the user's settings.

    :param db: Database.
    :param data: A dictionary with the entered data.
    :param user_id: The user's ID.
    """
    collection = db.get_collection("users_settings")
    await collection.update_one({"user_id": user_id}, {"$set": data}, upsert=True)


async def get_settings_user_by_id(user_id: int, db: AsyncIOMotorDatabase) -> dict:
    """
    Get the user's settings.

    :param db: Database.
    :param user_id: The user's ID.
    """
    collection = db.get_collection("users_settings")
    data: dict | None = await collection.find_one({"user_id": user_id})

    if data is not None:
        return data
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail={"result": False, "description": "Пользователь не найден."},
    )


async def delete_settings(user_id, db: AsyncIOMotorDatabase) -> None:
    """
    Delete the records from the database by user ID.

    :param db: Database.
    :param user_id: The telegram ID.
    """
    try:
        collection = db.get_collection("users_settings")
        await collection.delete_one({"user_id": user_id})

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"result": False, "description": "Пользователь не найден."},
        )
