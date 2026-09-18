from django.urls import path

from .views import (
    MyNotificationsView,
    NotificationDetailView,
)

urlpatterns = [
    path(
        "",
        MyNotificationsView.as_view(),
        name="my-notifications",
    ),
    path(
        "<uuid:pk>/",
        NotificationDetailView.as_view(),
        name="notification-detail",
    ),
]