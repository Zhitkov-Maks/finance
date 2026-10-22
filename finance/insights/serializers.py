from rest_framework import serializers

from .models import Insight


class InsightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Insight
        fields = (
            "id",
            "insight_type",
            "severity",
            "title",
            "message",
            "data",
            "action_url",
            "is_dismissed",
            "is_read",
            "created_at",
        )
        read_only_fields = fields
