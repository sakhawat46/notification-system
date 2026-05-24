from celery import shared_task
from .models import Notification


@shared_task(bind=True)
def send_notification_task(self, notification_id):

    notification = Notification.objects.get(id=notification_id)

    try:

        if notification.status == "PERMANENTLY_FAILED":
            return

        notification.status = "PROCESSING"
        notification.save(update_fields=["status"])

        """
        Your actual notification sending logic
        Example:
        - Email
        - SMS
        - Push notification
        """

        # simulate success
        success = True

        if success:
            notification.status = "SENT"

        else:
            raise Exception("Notification sending failed")

        notification.save(update_fields=["status"])

    except Exception as e:

        notification.retry_count += 1
        notification.last_error = str(e)

        if notification.retry_count >= 3:
            notification.status = "PERMANENTLY_FAILED"
        else:
            notification.status = "FAILED"

        notification.save()