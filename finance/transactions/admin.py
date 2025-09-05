from django.contrib import admin

from .models import Transaction, Category


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display: tuple = (
        "id",
        "amount",
        "user__email",
        "category__name",
        "account__name",
    )
    list_filter: tuple = "user__email",
    list_display_links: tuple = "category__name",


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display: tuple = "name", "type_transaction", "user__email"
