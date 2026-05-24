from django.urls import path

from .views import (
    NotificationListCreateAPIView,
    NotificationDetailAPIView,
    RetryNotificationAPIView,
)

urlpatterns = [
    path("notifications/", NotificationListCreateAPIView.as_view(), name="notification-list-create"),
    path("notifications/<uuid:notification_id>/", NotificationDetailAPIView.as_view(), name="notification-detail"),
    path("notifications/<uuid:notification_id>/retry/", RetryNotificationAPIView.as_view(), name="retry-notification"),
]