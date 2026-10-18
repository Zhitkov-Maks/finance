from rest_framework import serializers

from .models import Budget


class BudgetSerializer(serializers.ModelSerializer):
    category_name = serializers.SerializerMethodField()

    class Meta:
        model = Budget
        fields = (
            "id",
            "category",
            "category_name",
            "amount",
            "period_type",
            "is_active",
            "created_at",
        )
        read_only_fields = ("id", "created_at")
        extra_kwargs = {
            "category": {"required": False, "allow_null": True},
        }

    def get_category_name(self, obj):
        return obj.category.name if obj.category else "Общий бюджет"

    def validate_category(self, value):
        if value is None:
            return None
        request = self.context["request"]
        if value.user_id != request.user.id:
            raise serializers.ValidationError("Категория не принадлежит пользователю")
        if value.type_transaction != "expense":
            raise serializers.ValidationError(
                "Бюджеты можно ставить только на категории расходов"
            )
        return value

    def validate_amount(self, value):
        if value is None or value <= 0:
            raise serializers.ValidationError("Сумма бюджета должна быть положительной")
        return value

    def validate(self, attrs):
        user = self.context["request"].user

        category = attrs.get("category", serializers.empty)
        if category is serializers.empty:
            category = self.instance.category if self.instance else None

        period_type = attrs.get("period_type") or (
            self.instance.period_type if self.instance else Budget.PERIOD_MONTHLY
        )

        qs = Budget.objects.filter(user=user, period_type=period_type)
        if category is None:
            qs = qs.filter(category__isnull=True)
        else:
            qs = qs.filter(category=category)

        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            msg = (
                "Общий бюджет на этот период уже создан"
                if category is None
                else "Бюджет для этой категории и периода уже существует"
            )
            raise serializers.ValidationError(msg)

        return attrs
