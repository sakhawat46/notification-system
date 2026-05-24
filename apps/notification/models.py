import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Notification(models.Model):

    class Status(models.TextChoices):
        PENDING = "PENDING"
        SCHEDULED = "SCHEDULED"
        PROCESSING = "PROCESSING"
        SENT = "SENT"
        FAILED = "FAILED"
        PERMANENTLY_FAILED = "PERMANENTLY_FAILED"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    title = models.CharField(max_length=255)
    message = models.TextField()

    scheduled_time = models.DateTimeField()

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PENDING
    )

    retry_count = models.PositiveIntegerField(default=0)

    last_error = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_retry_allowed(self):
        return self.retry_count < 3