# Generated by Django 5.1.5 on 2025-03-03 17:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("accounts", "0007_remove_transfer_destination_account_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Transfer",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("amount", models.DecimalField(decimal_places=2, max_digits=10)),
                ("timestamp", models.DateTimeField()),
                (
                    "destination_account",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="transfers_in",
                        to="accounts.account",
                    ),
                ),
                (
                    "source_account",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="transfers_out",
                        to="accounts.account",
                    ),
                ),
            ],
            options={
                "verbose_name": "перевод",
                "verbose_name_plural": "переводы",
                "ordering": ["timestamp"],
            },
        ),
    ]
