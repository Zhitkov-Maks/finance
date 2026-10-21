import logging

from .models import Notification, NotificationPreferences

logger = logging.getLogger(__name__)


def get_prefs(user) -> NotificationPreferences:
    prefs, _ = NotificationPreferences.objects.get_or_create(user=user)
    return prefs


def create_notification(user, notification_type, title, message, data=None):
    """Создаёт уведомление; если push включён — ставит задачу на отправку."""
    prefs = get_prefs(user)

    notif = Notification.objects.create(
        user=user,
        notification_type=notification_type,
        title=title,
        message=message,
        data=data or {},
    )

    if prefs.push_enabled:
        from .tasks import send_push_notification

        send_push_notification.delay(str(notif.id))

    return notif
