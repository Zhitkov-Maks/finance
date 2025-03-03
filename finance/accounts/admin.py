from django.contrib import admin

from .models import Account


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display: tuple = "id", "name", "balance", "user__email"
    list_filter: tuple = ("user__email",)
    list_display_links: tuple = ("name",)
