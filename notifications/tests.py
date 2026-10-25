
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from accounts.models import CustomUser
from .models import Notification


class NotificationAPITests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="candidate1@example.com",
            username="candidate1",
            first_name="Candidate",
            last_name="One",
            password="TestPass123!",
        )

        self.other_user = CustomUser.objects.create_user(
            email="candidate2@example.com",
            username="candidate2",
            first_name="Candidate",
            last_name="Two",
            password="TestPass123!",
        )

        self.client.force_authenticate(user=self.user)

        self.my_notification = Notification.objects.create(
            recipient=self.user,
            notification_type=Notification.NotificationType.SYSTEM,
            title="My notification",
            message="This notification belongs to me.",
        )

        self.other_notification = Notification.objects.create(
            recipient=self.other_user,
            notification_type=Notification.NotificationType.SYSTEM,
            title="Other notification",
            message="This notification belongs to another user.",
        )

    def test_user_lists_only_their_own_notifications(self):
        response = self.client.get(reverse("my-notifications"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data
        if isinstance(results, dict) and "results" in results:
            results = results["results"]

        notification_ids = {item["id"] for item in results}

        self.assertIn(str(self.my_notification.id), notification_ids)
        self.assertNotIn(str(self.other_notification.id), notification_ids)

    def test_user_cannot_retrieve_another_users_notification(self):
        response = self.client.get(
            reverse(
                "notification-detail",
                kwargs={"pk": self.other_notification.id},
            )
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_can_mark_their_notification_as_read(self):
        response = self.client.patch(
            reverse(
                "notification-read",
                kwargs={"pk": self.my_notification.id},
            ),
            {},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.my_notification.refresh_from_db()
        self.assertTrue(self.my_notification.is_read)

    def test_user_cannot_mark_another_users_notification_as_read(self):
        response = self.client.patch(
            reverse(
                "notification-read",
                kwargs={"pk": self.other_notification.id},
            ),
            {},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.other_notification.refresh_from_db()
        self.assertFalse(self.other_notification.is_read)

    def test_mark_all_read_only_updates_current_users_notifications(self):
        response = self.client.patch(
            reverse("notifications-read-all"),
            {},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["updated_count"], 1)

        self.my_notification.refresh_from_db()
        self.other_notification.refresh_from_db()

        self.assertTrue(self.my_notification.is_read)
        self.assertFalse(self.other_notification.is_read)

    def test_unauthenticated_user_cannot_list_notifications(self):
        anonymous_client = APIClient()

        response = anonymous_client.get(
            reverse("my-notifications")
        )

        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )
    def test_user_can_filter_unread_notifications(self):
        response = self.client.get(
            reverse("my-notifications"),
            {"is_read": "false"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data
        if isinstance(results, dict) and "results" in results:
            results = results["results"]

        notification_ids = {item["id"] for item in results}

        self.assertIn(str(self.my_notification.id), notification_ids)
        self.assertNotIn(str(self.other_notification.id), notification_ids)

    def test_user_can_filter_read_notifications(self):
        self.my_notification.is_read = True
        self.my_notification.save(update_fields=["is_read"])

        response = self.client.get(
            reverse("my-notifications"),
            {"is_read": "true"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data
        if isinstance(results, dict) and "results" in results:
            results = results["results"]

        notification_ids = {item["id"] for item in results}

        self.assertIn(str(self.my_notification.id), notification_ids)
        self.assertNotIn(str(self.other_notification.id), notification_ids)

    def test_unread_count_only_includes_current_users_notifications(self):
        response = self.client.get(
            reverse("notifications-unread-count")
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["unread_count"], 1)

    def test_notification_detail_does_not_allow_updates(self):
        response = self.client.patch(
            reverse(
                "notification-detail",
                kwargs={"pk": self.my_notification.id},
            ),
            {"is_read": True},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )

        self.my_notification.refresh_from_db()
        self.assertFalse(self.my_notification.is_read)
