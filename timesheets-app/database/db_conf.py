"""We describe the connection to the database."""

import asyncio
import logging
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure

from config import DB_MONGO_NAME, DB_MONGO_PASS

logger = logging.getLogger(__name__)

MONGO_URI = f"mongodb://{DB_MONGO_NAME}:{DB_MONGO_PASS}@mongodb"


class MongoDB:
    _instance = None
    _client: Optional[AsyncIOMotorClient] = None
    _db: Optional[AsyncIOMotorDatabase] = None
    _is_connected = False
    _reconnect_lock = asyncio.Lock()
    _retry_count = 3
    _retry_delay = 1  # секунд

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._client is None:
            self._connect()

    def _connect(self):
        """Создает новое соединение с базой данных."""
        try:
            self._client = AsyncIOMotorClient(
                MONGO_URI,
                maxPoolSize=100,
                minPoolSize=10,
                connectTimeoutMS=5000,
                serverSelectionTimeoutMS=5000,
                socketTimeoutMS=30000,
                # Автоматическое переподключение
                retryWrites=True,
                retryReads=True,
            )
            self._db = self._client[DB_MONGO_NAME]
            self._is_connected = True
            logger.info("Successfully connected to MongoDB")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            self._is_connected = False
            raise

    async def ensure_connection(self) -> bool:
        """
        Проверяет соединение и переподключает при необходимости.
        Возвращает True если соединение установлено.
        """
        async with self._reconnect_lock:
            if self._is_connected:
                try:
                    # Проверяем, живое ли соединение
                    await self._client.admin.command("ping")
                    return True
                except (ServerSelectionTimeoutError, ConnectionFailure) as e:
                    logger.warning(f"Connection lost, reconnecting... {e}")
                    self._is_connected = False

            # Пытаемся переподключиться
            for attempt in range(self._retry_count):
                try:
                    logger.info(
                        f"Reconnection attempt {attempt + 1}/{self._retry_count}"
                    )
                    self._client = AsyncIOMotorClient(
                        MONGO_URI,
                        maxPoolSize=100,
                        minPoolSize=10,
                        connectTimeoutMS=5000,
                        serverSelectionTimeoutMS=5000,
                        socketTimeoutMS=30000,
                        retryWrites=True,
                        retryReads=True,
                    )
                    self._db = self._client[DB_MONGO_NAME]
                    # Проверяем новое соединение
                    await self._client.admin.command("ping")
                    self._is_connected = True
                    logger.info("Successfully reconnected to MongoDB")
                    return True
                except Exception as e:
                    logger.error(f"Reconnection attempt {attempt + 1} failed: {e}")
                    if attempt < self._retry_count - 1:
                        await asyncio.sleep(self._retry_delay * (attempt + 1))
                    else:
                        logger.error("All reconnection attempts failed")
                        return False
            return False

    def get_client(self) -> AsyncIOMotorClient:
        """Возвращает клиент MongoDB."""
        return self._client

    def get_db(self) -> AsyncIOMotorDatabase:
        """Возвращает базу данных."""
        return self._db

    async def close(self):
        """Закрывает соединение с базой данных."""
        if self._client:
            self._client.close()
            self._client = None
            self._db = None
            self._is_connected = False
            logger.info("MongoDB connection closed")


mongodb = MongoDB()


async def get_db():
    """
    Возвращает экземпляр базы данных с проверкой соединения.
    """
    if not await mongodb.ensure_connection():
        raise ConnectionError("Unable to connect to MongoDB")
    return mongodb.get_db()
