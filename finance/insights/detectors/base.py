import logging
from decimal import Decimal

from asgiref.sync import sync_to_async

from insights.services import create_insight

logger = logging.getLogger(__name__)


async def _alist(qs) -> list:
    return [obj async for obj in qs]


async def _aaggregate(qs, **kwargs) -> dict:
    return await sync_to_async(qs.aggregate)(**kwargs)


async def _save_insight(**kwargs) -> bool:
    return await sync_to_async(create_insight)(**kwargs)


def _to_decimal(value) -> Decimal:
    return value if value is not None else Decimal("0")
