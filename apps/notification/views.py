from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from kombu.exceptions import OperationalError

from .models import Notification
from .serializers import NotificationSerializer
from .tasks import send_notification_task


def enqueue_notification(notification, eta=None):
    try:
        if eta is not None:
            send_notification_task.apply_async(
                args=[str(notification.id)],
                eta=eta
            )
        else:
            send_notification_task.delay(str(notification.id))
        return True
    except OperationalError as exc:
        notification.status = Notification.Status.FAILED
        notification.last_error = (
            "Notification broker is unavailable. "
            "Start Redis and retry."
        )
        notification.save(update_fields=["status", "last_error", "updated_at"])
        return False



class NotificationListCreateAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        notifications = Notification.objects.filter(
            user=request.user
        ).order_by("-created_at")

        serializer = NotificationSerializer(
            notifications,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def post(self, request):

        serializer = NotificationSerializer(
            data=request.data
        )

        if serializer.is_valid():

            notification = serializer.save(
                user=request.user,
                status=Notification.Status.SCHEDULED
            )

            queued = enqueue_notification(
                notification=notification,
                eta=notification.scheduled_time
            )

            if not queued:
                return Response(
                    {
                        "error": (
                            "Notification was saved, but it could not be queued "
                            "because the message broker is not running."
                        ),
                        "data": NotificationSerializer(notification).data
                    },
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )

            return Response(
                {
                    "message": "Notification scheduled successfully.",
                    "data": NotificationSerializer(notification).data
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )



class NotificationDetailAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, notification_id):

        try:
            notification = Notification.objects.get(
                id=notification_id,
                user=request.user
            )

        except Notification.DoesNotExist:

            return Response(
                {
                    "error": "Notification not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = NotificationSerializer(notification)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )



class RetryNotificationAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, notification_id):

        try:
            notification = Notification.objects.get(
                id=notification_id,
                user=request.user
            )

        except Notification.DoesNotExist:

            return Response(
                {
                    "error": "Notification not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        if notification.status != Notification.Status.FAILED:

            return Response(
                {
                    "error": "Only failed notifications can be retried."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if notification.retry_count >= 3:

            return Response(
                {
                    "error": "Retry limit exceeded."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        notification.status = Notification.Status.SCHEDULED
        notification.last_error = ""
        notification.save(update_fields=["status", "last_error", "updated_at"])

        queued = enqueue_notification(notification=notification)

        if not queued:
            return Response(
                {
                    "error": (
                        "Retry could not be queued because the message broker "
                        "is not running."
                    ),
                    "data": NotificationSerializer(notification).data
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        return Response(
            {
                "message": "Retry started successfully."
            },
            status=status.HTTP_200_OK
        )
