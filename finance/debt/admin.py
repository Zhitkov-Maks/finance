from django.contrib import admin

from .models import Debt


@admin.register(Debt)
class DebtAdmin(admin.ModelAdmin):
    list_display: tuple = (
        "id",
        "transfer",
        "borrower_description",
        "transfer__source_account",
        "transfer__destination_account",
        "transfer__amount",
    )
