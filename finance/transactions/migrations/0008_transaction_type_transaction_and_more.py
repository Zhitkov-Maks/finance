from django.db import migrations, models


def backfill_type_transaction(apps, schema_editor):
    """
    Заполняет type_transaction через Raw SQL, так как Django ORM
    не поддерживает UPDATE с JOIN в F-выражениях.
    """
    schema_editor.execute("""
        UPDATE transactions
        SET type_transaction = c.type_transaction
        FROM transactions_category c
        WHERE transactions.category_id = c.id
    """)

    schema_editor.execute("""
        UPDATE transactions
        SET type_transaction = 'expense'
        WHERE category_id IS NULL OR type_transaction IS NULL
    """)


class Migration(migrations.Migration):
    dependencies = [
        (
            "transactions",
            "0007_remove_category_transaction_level_50b283_idx_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="transaction",
            name="type_transaction",
            field=models.CharField(
                choices=[("income", "Доход"), ("expense", "Расход")],
                db_index=True,
                max_length=10,
                null=True,
                verbose_name="Тип операции",
            ),
        ),
        migrations.RunPython(backfill_type_transaction, migrations.RunPython.noop),
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
