# Generated by Django 5.1.5 on 2025-03-06 18:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("expenses", "0002_alter_expense_create_at"),
    ]

    operations = [
        migrations.AddField(
            model_name="expense",
            name="comment",
            field=models.TextField(
                default="", max_length=200, verbose_name="Комментарий"
            ),
        ),
    ]
