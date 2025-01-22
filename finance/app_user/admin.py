from django.contrib import admin

from .models import CustomUser


@admin.register(CustomUser)
class UserRegister(admin.ModelAdmin):
    list_display: tuple = ("id", "email",)
    list_display_links: tuple = ("email",)
