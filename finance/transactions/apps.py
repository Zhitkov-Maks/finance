from django.apps import AppConfig


class TransactionsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "transactions"

    def ready(self):
        # Импорт сигналов для их регистрации при старте Django
        import transactions.signals  # noqa: F401
