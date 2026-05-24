from rest_framework import serializers
from django.utils import timezone

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification
        fields = [
            "id",
            "title",
            "message",
            "scheduled_time",
            "status",
            "retry_count",
            "last_error",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "status",
            "retry_count",
            "last_error",
            "created_at",
            "updated_at",
        ]

    def validate_scheduled_time(self, value):

        if value <= timezone.now():
            raise serializers.ValidationError(
                "Scheduled time must be in the future."
            )

        return value