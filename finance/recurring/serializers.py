from rest_framework import serializers

from .models import RecurringTransaction


class RecurringTransactionSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    account_name = serializers.CharField(source="account.name", read_only=True)
    schedule_display = serializers.CharField(
        source="get_schedule_type_display", read_only=True
    )
    type_display = serializers.CharField(
        source="get_type_transaction_display", read_only=True
    )

    class Meta:
        model = RecurringTransaction
        fields = (
            "id",
            "title",
            "account",
            "account_name",
            "category",
            "category_name",
            "type_transaction",
            "type_display",
            "amount",
            "comment",
            "schedule_type",
            "schedule_display",
            "day_of_month",
            "weekday",
            "start_date",
            "end_date",
            "next_run_date",
            "last_run_date",
            "is_active",
            "created_at",
        )
        read_only_fields = ("id", "last_run_date", "created_at")

    def validate(self, attrs):
        user = self.context["request"].user
        category = attrs.get("category")
        account = attrs.get("account")

        if category and category.user_id != user.id:
            raise serializers.ValidationError({"category": "Категория не ваша"})
        if account and account.user_id != user.id:
            raise serializers.ValidationError({"account": "Счет не ваш"})

        return attrs


class UpcomingPaymentSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    type_transaction = serializers.CharField()
    category_name = serializers.CharField()
    account_name = serializers.CharField()
    date = serializers.DateField()
