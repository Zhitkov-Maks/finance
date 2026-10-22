import logging

from notifications.models import NotificationPreferences
from notifications.services import create_notification

from .models import Insight

logger = logging.getLogger(__name__)


def create_insight(
    user,
    insight_type,
    severity,
    title,
    message,
    data=None,
    action_url="",
    period_key="",
):
    """
    Создаёт инсайт и опционально отправляет push через существующую систему.
    Дедуплицирует по period_key (уникальный в рамках пользователя).
    """
    if period_key and Insight.objects.filter(user=user, period_key=period_key).exists():
        return None

    insight = Insight.objects.create(
        user=user,
        insight_type=insight_type,
        severity=severity,
        title=title,
        message=message,
        data=data or {},
        action_url=action_url,
        period_key=period_key,
    )

    # Push-уведомление через уже существующий сервис notifications
    prefs = NotificationPreferences.objects.filter(user=user).first()
    if prefs is None or prefs.insight_alerts:
        try:
            create_notification(
                user=user,
                notification_type="insight_alert",
                title=title,
                message=message,
                data={
                    "insight_id": str(insight.id),
                    "url": action_url or "/",
                    "insight_type": insight_type,
                    "severity": severity,
                },
            )
        except Exception as e:
            logger.exception("Failed to send push for insight: %s", e)

    return insight
