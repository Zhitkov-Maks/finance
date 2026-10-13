import hashlib

from django.core.cache import cache

BALANCE_HISTORY_CACHE_TTL = 60 * 60


def balance_history_version_key(user_id: int) -> str:
    return f"balance_history_version:{user_id}"


def make_balance_history_cache_key(
    user_id, date_from, date_to, account_id, include_inactive
):
    version = cache.get(balance_history_version_key(user_id), 0)
    raw = (
        f"balance_history:{user_id}:v{version}:"
        f"{date_from}:{date_to}:"
        f"{account_id or 'all'}:{int(include_inactive)}"
    )
    digest = hashlib.md5(raw.encode()).hexdigest()[:16]
    return f"balance_history:{user_id}:{digest}"


def invalidate_balance_history_cache(user_id: int) -> None:
    version_key = balance_history_version_key(user_id)
    try:
        cache.incr(version_key)
    except ValueError:
        cache.set(version_key, 1, timeout=None)
