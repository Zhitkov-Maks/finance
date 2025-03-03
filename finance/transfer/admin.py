from django.contrib import admin
from .models import Transfer


@admin.register(Transfer)
class AccountAdmin(admin.ModelAdmin):
    list_display: tuple = (
        "id",
        "source_account",
        "destination_account",
        "amount",
        "timestamp",
    )
