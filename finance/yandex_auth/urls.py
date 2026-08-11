from django.urls import path
from .views import YandexCallbackView, yandex_login

urlpatterns = [
    path('login/', yandex_login, name='yandex-login'),
    path('callback/', YandexCallbackView.as_view(), name='yandex-callback'),
]
