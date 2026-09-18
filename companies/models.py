import uuid

from django.db import models


class Company(models.Model):

    class CompanySize(models.TextChoices):
        STARTUP = "STARTUP", "Startup"
        SMALL = "SMALL", "Small"
        MEDIUM = "MEDIUM", "Medium"
        LARGE = "LARGE", "Large"
        ENTERPRISE = "ENTERPRISE", "Enterprise"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    name = models.CharField(
        max_length=255,
        unique=True,
    )

    slug = models.SlugField(
        max_length=255,
        unique=True,
    )

    email = models.EmailField(
        unique=True,
    )

    website = models.URLField(
        blank=True,
    )

    industry = models.CharField(
        max_length=150,
    )

    company_size = models.CharField(
        max_length=20,
        choices=CompanySize.choices,
    )

    founded_year = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    headquarters = models.CharField(
        max_length=255,
        blank=True,
    )

    description = models.TextField(
        blank=True,
    )

    logo = models.ImageField(
        upload_to="company_logos/",
        blank=True,
        null=True,
    )

    linkedin_url = models.URLField(
        blank=True,
    )

    twitter_url = models.URLField(
        blank=True,
    )

    facebook_url = models.URLField(
        blank=True,
    )

    is_verified = models.BooleanField(
        default=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        db_table = "companies"
        ordering = ["name"]
        verbose_name = "Company"
        verbose_name_plural = "Companies"

    def __str__(self):
        return self.name