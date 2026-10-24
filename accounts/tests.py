
from django.test import TestCase

from accounts.models import CustomUser


class CustomUserManagerTests(TestCase):
    """Tests for creating regular users and superusers."""

    def setUp(self):
        self.user_data = {
            "email": "TestUser@EXAMPLE.COM",
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
        }

    def test_create_user_normalizes_email(self):
        user = CustomUser.objects.create_user(
            **self.user_data,
            password="StrongPass123!",
        )

        # Django normalizes the domain portion of the email.
        self.assertEqual(user.email, "TestUser@example.com")

    def test_create_user_hashes_password(self):
        user = CustomUser.objects.create_user(
            **self.user_data,
            password="StrongPass123!",
        )

        self.assertNotEqual(user.password, "StrongPass123!")
        self.assertTrue(user.check_password("StrongPass123!"))
        self.assertFalse(user.check_password("WrongPassword123!"))

    def test_create_user_uses_expected_defaults(self):
        user = CustomUser.objects.create_user(
            **self.user_data,
            password="StrongPass123!",
        )

        self.assertEqual(user.role, CustomUser.Role.CANDIDATE)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_verified)

    def test_create_user_without_email_raises_error(self):
        with self.assertRaisesMessage(
            ValueError,
            "Users must have an email address.",
        ):
            CustomUser.objects.create_user(
                email="",
                password="StrongPass123!",
                username="noemail",
                first_name="No",
                last_name="Email",
            )

    def test_create_superuser_sets_expected_permissions(self):
        admin = CustomUser.objects.create_superuser(
            email="admin@example.com",
            password="AdminPass123!",
            username="admin",
            first_name="HireNext",
            last_name="Admin",
        )

        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.is_active)
        self.assertTrue(admin.is_verified)
        self.assertEqual(admin.role, CustomUser.Role.ADMIN)
        self.assertTrue(admin.check_password("AdminPass123!"))

    def test_create_superuser_rejects_is_staff_false(self):
        with self.assertRaisesMessage(
            ValueError,
            "Superuser must have is_staff=True.",
        ):
            CustomUser.objects.create_superuser(
                email="admin@example.com",
                password="AdminPass123!",
                username="admin",
                first_name="HireNext",
                last_name="Admin",
                is_staff=False,
            )

    def test_create_superuser_rejects_is_superuser_false(self):
        with self.assertRaisesMessage(
            ValueError,
            "Superuser must have is_superuser=True.",
        ):
            CustomUser.objects.create_superuser(
                email="admin@example.com",
                password="AdminPass123!",
                username="admin",
                first_name="HireNext",
                last_name="Admin",
                is_superuser=False,
            )
