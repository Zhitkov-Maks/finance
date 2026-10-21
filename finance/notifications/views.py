from django.conf import settings
from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Notification, NotificationPreferences, PushSubscription
from .serializers import NotificationPreferencesSerializer, NotificationSerializer


@extend_schema(tags=["Notifications"])
class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        qs = Notification.objects.filter(user=self.request.user)
        if self.request.query_params.get("unread") == "1":
            qs = qs.filter(is_read=False)
        return qs


@extend_schema(tags=["Notifications"])
class NotificationReadView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk):
        Notification.objects.filter(user=request.user, pk=pk).update(is_read=True)
        return Response(status=204)


@extend_schema(tags=["Notifications"])
class NotificationReadAllView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        Notification.objects.filter(user=request.user, is_read=False).update(
            is_read=True
        )
        return Response(status=204)


@extend_schema(tags=["Notifications"])
class NotificationPreferencesView(generics.RetrieveUpdateAPIView):
    serializer_class = NotificationPreferencesSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        prefs, _ = NotificationPreferences.objects.get_or_create(user=self.request.user)
        return prefs


@extend_schema(tags=["Notifications"])
class PushSubscribeView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        data = request.data
        PushSubscription.objects.update_or_create(
            endpoint=data["endpoint"],
            defaults={
                "user": request.user,
                "p256dh": data["keys"]["p256dh"],
                "auth": data["keys"]["auth"],
                "user_agent": request.META.get("HTTP_USER_AGENT", "")[:255],
            },
        )
        return Response(status=201)


@extend_schema(tags=["Notifications"])
class PushUnsubscribeView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        PushSubscription.objects.filter(
            user=request.user, endpoint=request.data.get("endpoint")
        ).delete()
        return Response(status=204)


@extend_schema(tags=["Notifications"])
class VapidPublicKeyView(APIView):
    """
    Отдаёт VAPID public key для подписки на Web Push.
    Не требует авторизации — ключ публичный.
    """

    permission_classes = ()  # AllowAny
    authentication_classes = ()

    def get(self, request):
        return Response({"public_key": settings.VAPID_PUBLIC_KEY})


@extend_schema(tags=["Notifications"])
class NotificationDeleteView(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


@extend_schema(tags=["Notifications"])
class NotificationClearReadView(APIView):
    """Удаляет все прочитанные уведомления пользователя"""

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        Notification.objects.filter(user=request.user, is_read=True).delete()
        return Response(status=204)
