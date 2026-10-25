from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Notification
from .serializers import NotificationSerializer


class MyNotificationsView(generics.ListAPIView):
    """
    List notifications belonging to the authenticated user.

    Optional query parameter:
    ?is_read=true
    ?is_read=false
    """

    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Notification.objects.filter(
            recipient=self.request.user
        ).select_related(
            "related_job",
            "related_application",
        )

        is_read = self.request.query_params.get("is_read")

        if is_read == "true":
            queryset = queryset.filter(is_read=True)
        elif is_read == "false":
            queryset = queryset.filter(is_read=False)

        return queryset


class NotificationDetailView(generics.RetrieveAPIView):
    """
    Retrieve a notification belonging to the authenticated user.
    """

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
    Mark one of the authenticated user's notifications as read.
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
        notification.save(update_fields=["is_read"])

        serializer = self.get_serializer(notification)

        return Response(serializer.data, status=200)


class MarkAllNotificationsReadView(generics.GenericAPIView):
    """
    Mark all unread notifications of the authenticated user as read.
    """

    permission_classes = [IsAuthenticated]
    http_method_names = ["patch"]

    def patch(self, request, *args, **kwargs):
        updated_count = Notification.objects.filter(
            recipient=request.user,
            is_read=False,
        ).update(is_read=True)

        return Response(
            {
                "detail": "All notifications marked as read.",
                "updated_count": updated_count,
            },
            status=200,
        )


class UnreadNotificationCountView(generics.GenericAPIView):
    """
    Return the unread notification count for the authenticated user.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        unread_count = Notification.objects.filter(
            recipient=request.user,
            is_read=False,
        ).count()

        return Response({"unread_count": unread_count}, status=200)
