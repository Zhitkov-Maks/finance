import random
import string
from urllib.parse import urlencode
import requests
import logging

from django.conf import settings
from django.http import HttpResponseRedirect
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from djoser.utils import login_user

from app_user.models import CustomUser

# Настройка логирования
logger = logging.getLogger(__name__)

User: CustomUser = get_user_model()

YANDEX_AUTH_URL = "https://oauth.yandex.ru/authorize"
YANDEX_TOKEN_URL = "https://oauth.yandex.ru/token"
YANDEX_INFO_URL = "https://login.yandex.ru/info"


def yandex_login(request) -> HttpResponseRedirect:
    """Function for processing /login."""
    params: dict = {
        "response_type": "code",
        "client_id": settings.YANDEX_CLIENT_ID,
        "redirect_uri": request.build_absolute_uri("/auth/yandex/callback/"),
        "scope": "login:info login:email",
    }
    url = f"{YANDEX_AUTH_URL}?{urlencode(params)}"
    return HttpResponseRedirect(url)


class YandexCallbackView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def _exchange_code_for_access_token(self, code: str) -> dict | Response:
        """Request user data from Yandex."""
        redirect_uri: str = self.request.build_absolute_uri("/auth/yandex/callback/")
        try:
            request: requests.Response = requests.post(
                YANDEX_TOKEN_URL,
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "client_id": settings.YANDEX_CLIENT_ID,
                    "client_secret": settings.YANDEX_CLIENT_SECRET,
                    "redirect_uri": redirect_uri,
                },
                timeout=10,
            )
            request.raise_for_status()
            logger.info(f"Token exchange successful")
            return request.json()

        except Exception as e:
            logger.error(f"Yandex token exchange failed: {e}")
            return Response(
                {"detail": "yandex token exchange failed"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _get_profile(self, token_data: dict):
        """Get the user's profile."""
        yandex_access_token = token_data.get("access_token")
        if not yandex_access_token:
            logger.error("No access_token from Yandex")
            return Response(
                {"detail": "no access_token from Yandex"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        try:
            request: requests.Response = requests.get(
                YANDEX_INFO_URL,
                headers={"Authorization": f"OAuth {yandex_access_token}"},
                timeout=10,
            )
            request.raise_for_status()
            return request.json()

        except Exception as e:
            logger.error(f"Yandex profile fetch failed: {e}")
            return Response(
                {"detail": "yandex profile fetch failed"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _user_extraction(self, yandex_info: dict) -> tuple[int, str, str, str] | Response:
        """Extract user data."""
        yandex_id: int = yandex_info.get("id")
        email: str = yandex_info.get("default_email", "")
        first_name: str = yandex_info.get("first_name", "")
        last_name: str = yandex_info.get("last_name", "")
        logger.info(f"Yandex ID: {yandex_id}, Email: {email}")

        if not yandex_id:
            logger.error("No yandex_id in response")
            return Response(
                {"detail": "no yandex_id"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        if not email:
            logger.warning("No email from Yandex, using yandex_id as email")
            email = f"yandex_{yandex_id}@yandex.ru"
        return yandex_id, email, first_name, last_name

    def _create_new_user(self, user_data) -> CustomUser:
        yandex_id, email, first_name, last_name = user_data
        try:
            user = User.objects.create(
                email=email,
                first_name=first_name,
                last_name=last_name,
                yandex_id=yandex_id,
                is_active=True,
                is_verified=True,
                password=str(random.choice(string.ascii_letters) for i in range(20)),
            )
            logger.info(f"New user created successfully: ID={user.id}, Email={user.email}")
            return user

        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            return Response(
                {"detail": f"Failed to create user: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _search_user(self, user_data: tuple) -> CustomUser:
        """Search for a user in the database."""
        yandex_id, email, first_name, last_name = user_data
        try:
            user: CustomUser = User.objects.get(yandex_id=yandex_id)
            logger.info(f"User found by yandex_id: {user.email}")

            updated = False
            if user.email != email:
                user.email = email
                updated = True

            if user.first_name != first_name:
                user.first_name = first_name
                updated = True

            if user.last_name != last_name:
                user.last_name = last_name
                updated = True

            if updated:
                user.save()
                logger.info(f"Updated user data: {user.email}")
            return user

        except User.DoesNotExist:
            logger.info(f"User with yandex_id {yandex_id} not found")
            return self._create_new_user(user_data)

    def get(self, request):
        code: str = request.GET.get("code")
        if not code:
            return Response(
                {"detail": "code missing"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        token_data = self._exchange_code_for_access_token(code)
        yandex_info = self._get_profile(token_data)
        logger.info(f"Yandex user info: {yandex_info}")

        yandex_user = self._user_extraction(yandex_info)
        user: CustomUser = self._search_user(yandex_user)

        # Генерируем токен
        try:
            tokens = login_user(request, user)
            logger.info(f"Token generated successfully")
        except Exception as e:
            logger.error(f"Failed to generate token: {e}")
            return Response(
                {"detail": "Failed to generate token"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Редирект на фронтенд
        frontend_url = getattr(settings, 'FRONTEND_URL', "http://localhost")
        redirect_url = f"{frontend_url}/oauth-callback?token={tokens.key}"
        logger.info(f"Redirecting to: {redirect_url}")
        return HttpResponseRedirect(redirect_url)