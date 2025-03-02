from django.contrib import admin

from .models import Account, Debt, Transfer


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display: tuple = "id", "name", "balance", "user__email"
    list_filter: tuple = ("user__email",)
    list_display_links: tuple = ("name",)


@admin.register(Transfer)
class AccountAdmin(admin.ModelAdmin):
    list_display: tuple = (
        "id",
        "source_account",
        "destination_account",
        "amount",
        "timestamp",
    )


@admin.register(Debt)
class AccountAdmin(admin.ModelAdmin):
    list_display: tuple = (
        "id",
        "transfer",
        "borrower_description",
        "transfer__source_account",
        "transfer__destination_account",
        "transfer__amount",
    )
