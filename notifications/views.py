from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Notification
from .serializers import NotificationSerializer


class MyNotificationsView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(
            recipient=self.request.user
        ).select_related(
            "related_job",
            "related_application",
        )


class NotificationDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(
            recipient=self.request.user
        ).select_related(
            "related_job",
            "related_application",
        )
class MarkNotificationReadView(generics.UpdateAPIView):
    """
    Mark one notification as read.

    Users can only mark their own notifications as read.
    """

    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["patch"]

    def get_queryset(self):
        return Notification.objects.filter(
            recipient=self.request.user
        ).select_related(
            "related_job",
            "related_application",
        )

    def partial_update(self, request, *args, **kwargs):
        notification = self.get_object()

        notification.is_read = True
        notification.save(
            update_fields=["is_read"]
        )

        serializer = self.get_serializer(notification)

        return Response(
            serializer.data,
            status=200,
        )
class MarkAllNotificationsReadView(generics.GenericAPIView):
    """
    Mark all notifications of the logged-in user as read.
    """

    permission_classes = [IsAuthenticated]
    http_method_names = ["patch"]

    def patch(self, request, *args, **kwargs):

        updated_count = Notification.objects.filter(
            recipient=request.user,
            is_read=False,
        ).update(
            is_read=True
        )

        return Response(
            {
                "detail": "All notifications marked as read.",
                "updated_count": updated_count,
            },
            status=200,
        )