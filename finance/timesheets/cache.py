import logging

from django.core.cache import cache

logger = logging.getLogger(__name__)

CACHE_TTL = 60 * 60 * 24


def make_timesheets_key(user_id: int, *args) -> str:
    """
    Генерирует ключ кэша.
    Пример: make_timesheets_key(1, "shifts", 2026, 5) -> "timesheets:1:shifts:2026:5"
    """
    parts = [str(arg) for arg in args]
    return f"timesheets:{user_id}:{':'.join(parts)}"


def invalidate_timesheets_cache(user_id: int) -> None:
    """
    Полностью сбрасывает кэш графиков для конкретного пользователя.
    Вызывается при любых POST, PUT, DELETE, PATCH запросах.
    """
    try:
        cache.delete_pattern(f"timesheets:{user_id}:*")
    except Exception as e:
        logger.error(f"Failed to invalidate timesheets cache for user {user_id}: {e}")
