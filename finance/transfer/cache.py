"""
Кэширование аналитики переводов.

Ключ: transfers:analytics:{user_id}:{date_from}:{date_to}
При мутации любого перевода пользователя — все ключи этого user_id сбрасываются.
"""

from __future__ import annotations

from datetime import date
from typing import Any

from django.core.cache import cache

# TTL по умолчанию — 5 минут. Аналитика не критична к секундной точности,
# а пересчитывать её на каждый запрос дорого.
ANALYTICS_CACHE_TTL: int = 60 * 5

# Префикс ключа для версии пользователя. Меняя версию, мы «отменяем»
# все старые ключи аналитики разом — без необходимости их перечислять.
_VERSION_KEY = "transfers:analytics:version:{user_id}"


def _get_version(user_id: int) -> int:
    """Текущая версия кэша пользователя. Если нет — 1."""
    return cache.get(_VERSION_KEY.format(user_id=user_id), 1)


def _bump_version(user_id: int) -> int:
    """Инкрементирует версию. Все старые ключи становятся недоступны."""
    key = _VERSION_KEY.format(user_id=user_id)
    try:
        # redis-py поддерживает incr; для LocMemCache — тоже.
        return cache.incr(key)
    except ValueError:
        # Ключа нет — создаём
        cache.set(key, 2, timeout=None)
        return 2


def _analytics_key(user_id: int, date_from: date, date_to: date) -> str:
    version = _get_version(user_id)
    return (
        f"transfers:analytics:{user_id}:v{version}:"
        f"{date_from.isoformat()}:{date_to.isoformat()}"
    )


def get_analytics_cache(user_id: int, date_from: date, date_to: date) -> dict | None:
    """Возвращает закэшированную аналитику или None."""
    return cache.get(_analytics_key(user_id, date_from, date_to))


def set_analytics_cache(
    user_id: int,
    date_from: date,
    date_to: date,
    payload: dict[str, Any],
    ttl: int = ANALYTICS_CACHE_TTL,
) -> None:
    """Кладёт аналитику в кэш."""
    cache.set(
        _analytics_key(user_id, date_from, date_to),
        payload,
        timeout=ttl,
    )


def invalidate_transfer_analytics_cache(user_id: int) -> None:
    """
    Сбрасывает всю кэшированную аналитику пользователя.

    Вызывается из TransferFundsView / TransferDetailView при
    create / update / delete.
    """
    _bump_version(user_id)
