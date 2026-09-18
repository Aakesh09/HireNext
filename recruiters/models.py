import uuid
from django.conf import settings
from django.core.exceptions import ValidationError  # Added import
from django.db import models
from companies.models import Company

class RecruiterProfile(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="recruiter_profile",
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="recruiters",
    )
    designation = models.CharField(
        max_length=150,
    )
    department = models.CharField(
        max_length=150,
        blank=True,
    )
    employee_id = models.CharField(
        max_length=100,
        blank=True,
    )
    phone_number = models.CharField(
        max_length=15,
        blank=True,
    )
    linkedin_url = models.URLField(
        blank=True,
    )
    profile_picture = models.ImageField(
        upload_to="recruiter_profiles/",
        blank=True,
        null=True,
    )
    bio = models.TextField(
        blank=True,
    )
    is_primary_recruiter = models.BooleanField(
        default=False,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        db_table = "recruiter_profiles"
        ordering = ["-created_at"]
        verbose_name = "Recruiter Profile"
        verbose_name_plural = "Recruiter Profiles"

    def clean(self):
        super().clean()

        # 1. Validate user role
        if self.user_id:
            if self.user.role != "RECRUITER":
                raise ValidationError(
                    {
                        "user": (
                            "The selected user must have the RECRUITER role."
                        )
                    }
                )

        # 2. Validate single primary recruiter restriction
        if self.is_primary_recruiter and self.company_id:
            existing_primary = (
                RecruiterProfile.objects
                .filter(
                    company_id=self.company_id,
                    is_primary_recruiter=True,
                )
                .exclude(pk=self.pk)
                .exists()
            )

            if existing_primary:
                raise ValidationError(
                    {
                        "is_primary_recruiter": (
                            "This company already has a primary recruiter."
                        )
                    }
                )

    def __str__(self):
        return f"{self.user.email} - {self.company.name}"
