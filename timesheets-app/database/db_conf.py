"""We describe the connection to the database."""

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

from config import DB_MONGO_NAME, DB_MONGO_PASS


MONGO_URI = f"mongodb://{DB_MONGO_NAME}:{DB_MONGO_PASS}@mongodb"


class MongoDB:
    def __init__(self):
        if not isinstance(DB_MONGO_NAME, str):
            raise ValueError("DB_NAME must be a string")

        try:
            self.client = MongoClient(MONGO_URI)
            self.db = self.client[DB_MONGO_NAME]
        except ConnectionFailure:
            raise

    def get_collection(self, collection_name: str):
        return self.db[collection_name]

    def close(self):
        self.client.close()
