import django.db.models.deletion
from django.db import migrations, models


def backfill_recurring_source(apps, schema_editor):
    Transaction = apps.get_model("transactions", "Transaction")
    RecurringTransaction = apps.get_model("recurring", "RecurringTransaction")

    for rec in RecurringTransaction.objects.all():
        prefix = f"[Авто] {rec.title}."
        Transaction.objects.filter(
            user_id=rec.user_id,
            account_id=rec.account_id,
            comment__startswith=prefix,
            recurring_source__isnull=True,
        ).update(recurring_source=rec)


def reverse_backfill(apps, schema_editor):
    Transaction = apps.get_model("transactions", "Transaction")
    Transaction.objects.filter(recurring_source__isnull=False).update(
        recurring_source=None
    )


class Migration(migrations.Migration):
    dependencies = [
        ("transactions", "0008_transaction_type_transaction_and_more"),
        ("recurring", "0002_recurringtransaction_is_subscription"),
    ]

    operations = [
        migrations.AddField(
            model_name="transaction",
            name="recurring_source",
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="generated_transactions",
                to="recurring.recurringtransaction",
            ),
        ),
        # ✅ RunPython — ВТОРЫМ
        migrations.RunPython(backfill_recurring_source, reverse_backfill),
    ]
