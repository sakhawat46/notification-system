import logging

from celery import shared_task
from django.utils import timezone

from .models import Notification


logger = logging.getLogger(__name__)
MAX_RETRY_ATTEMPTS = 3


def deliver_notification(notification):
    """
    Placeholder delivery integration.
    Raise an exception to mark a delivery attempt as failed.
    """
    if "fail" in notification.title.lower():
        raise RuntimeError("Simulated notification provider failure.")


@shared_task(bind=True)
def send_notification_task(self, notification_id):
    try:
        notification = Notification.objects.get(id=notification_id)
    except Notification.DoesNotExist:
        logger.warning("Notification %s does not exist.", notification_id)
        return

    if notification.status == Notification.Status.PERMANENTLY_FAILED:
        logger.info(
            "Skipping permanently failed notification %s.", notification_id
        )
        return

    if notification.scheduled_time > timezone.now():
        logger.info(
            "Notification %s ran before its scheduled time; skipping.",
            notification_id,
        )
        return

    notification.status = Notification.Status.PROCESSING
    notification.last_error = ""
    notification.save(update_fields=["status", "last_error", "updated_at"])

    try:
        deliver_notification(notification)
    except Exception as exc:
        notification.retry_count += 1
        notification.last_error = str(exc)

        if notification.retry_count >= MAX_RETRY_ATTEMPTS:
            notification.status = Notification.Status.PERMANENTLY_FAILED
        else:
            notification.status = Notification.Status.FAILED

        notification.save(
            update_fields=["retry_count", "last_error", "status", "updated_at"]
        )

        logger.exception(
            "Notification %s failed on attempt %s.",
            notification_id,
            notification.retry_count,
        )
        raise

    notification.status = Notification.Status.SENT
    notification.save(update_fields=["status", "updated_at"])
    logger.info("Notification %s sent successfully.", notification_id)
