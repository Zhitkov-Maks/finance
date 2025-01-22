from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import EmailField

from .usermanager import CustomUserManager


class CustomUser(AbstractUser):
    """
    Наследуемся от AbstractUser для того, чтобы регистрировать
    пользователя по email.
    """

    username: None = None
    email: EmailField = models.EmailField(
        "email address", unique=True
    )

    USERNAME_FIELD: str = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def __len__(self):
        return CustomUser.objects.count()
