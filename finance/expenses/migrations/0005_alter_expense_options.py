# Generated by Django 5.1.5 on 2025-03-09 09:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("expenses", "0004_alter_expense_comment"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="expense",
            options={
                "ordering": ["-create_at", "category__name"],
                "verbose_name": "расход",
                "verbose_name_plural": "расходы",
            },
        ),
    ]
