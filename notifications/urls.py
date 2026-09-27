from django.urls import path

from .views import (
    MyNotificationsView,
    NotificationDetailView,
    MarkNotificationReadView,
    MarkAllNotificationsReadView,
)

urlpatterns = [
    path(
        "",
        MyNotificationsView.as_view(),
        name="my-notifications",
    ),
    path(
    "read-all/",
    MarkAllNotificationsReadView.as_view(),
    name="notifications-read-all",
    ),
    path(
    "<uuid:pk>/read/",
    MarkNotificationReadView.as_view(),
    name="notification-read",
    ),
    path(
        "<uuid:pk>/",
        NotificationDetailView.as_view(),
        name="notification-detail",
    ),
]