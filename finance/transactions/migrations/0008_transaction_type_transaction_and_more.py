from django.db import migrations, models
from django.db.models import CharField, F, Value


def backfill_type_transaction(apps, schema_editor):
    """
    Заполняет type_transaction на основе category.type_transaction.
    Для транзакций, которые потеряли категорию или у которых её не было,
    ставит дефолтное значение 'expense', чтобы миграция не упала на шаге NOT NULL.
    """
    Transaction = apps.get_model("transactions", "Transaction")

    # 1. Если категория есть — берем тип из неё
    Transaction.objects.filter(category__isnull=False).update(
        type_transaction=F("category__type_transaction")
    )

    # 2. Если категории нет (битые данные) — ставим 'expense'
    Transaction.objects.filter(category__isnull=True).update(
        type_transaction=Value("expense", output_field=CharField())
    )


class Migration(migrations.Migration):
    dependencies = [
        (
            "transactions",
            "0007_remove_category_transaction_level_50b283_idx_and_more",
        ),
    ]

    operations = [
        # 1. Добавляем поле пустым
        migrations.AddField(
            model_name="transaction",
            name="type_transaction",
            field=models.CharField(
                choices=[("income", "Доход"), ("expense", "Расход")],
                db_index=True,
                max_length=10,
                null=True,  # Временно
                verbose_name="Тип операции",
            ),
        ),
        # 2. Запускаем быстрый бэкфилл через UPDATE
        migrations.RunPython(backfill_type_transaction, migrations.RunPython.noop),
        # 3. Меняем категорию на SET_NULL
        migrations.AlterField(
            model_name="transaction",
            name="category",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.SET_NULL,
                related_name="transactions",
                to="transactions.category",
                verbose_name="Категория",
            ),
        ),
        # 4. Делаем type_transaction обязательным (NOT NULL)
        migrations.AlterField(
            model_name="transaction",
            name="type_transaction",
            field=models.CharField(
                choices=[("income", "Доход"), ("expense", "Расход")],
                db_index=True,
                max_length=10,
                verbose_name="Тип операции",
            ),
        ),
    ]
