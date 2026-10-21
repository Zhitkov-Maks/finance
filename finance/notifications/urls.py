from django.urls import path

from .views import (
    NotificationClearReadView,
    NotificationDeleteView,
    NotificationListView,
    NotificationPreferencesView,
    NotificationReadAllView,
    NotificationReadView,
    PushSubscribeView,
    PushUnsubscribeView,
    VapidPublicKeyView,
)

app_name = "notifications"

urlpatterns = [
    # Список уведомлений (?unread=1 — только непрочитанные)
    path("", NotificationListView.as_view(), name="list"),
    path("<uuid:pk>/", NotificationDeleteView.as_view(), name="delete"),
    path("<uuid:pk>/read/", NotificationReadView.as_view(), name="read"),
    path("read-all/", NotificationReadAllView.as_view(), name="read-all"),
    path("preferences/", NotificationPreferencesView.as_view(), name="preferences"),
    path("push/subscribe/", PushSubscribeView.as_view(), name="push-subscribe"),
    path("push/unsubscribe/", PushUnsubscribeView.as_view(), name="push-unsubscribe"),
    path("vapid-public-key/", VapidPublicKeyView.as_view(), name="vapid-public-key"),
    path("clear-read/", NotificationClearReadView.as_view(), name="clear-read"),
]
