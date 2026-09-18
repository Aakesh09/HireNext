import uuid
from django.core.exceptions import ValidationError
from django.db import models

from companies.models import Company
from recruiters.models import RecruiterProfile


class JobCategory(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    name = models.CharField(
        max_length=100,
        unique=True,
    )
    description = models.TextField(
        blank=True,
    )
    is_active = models.BooleanField(
        default=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        db_table = "job_categories"
        ordering = ["name"]
        verbose_name = "Job Category"
        verbose_name_plural = "Job Categories"

    def __str__(self):
        return self.name


class Job(models.Model):
    class EmploymentType(models.TextChoices):
        FULL_TIME = "FULL_TIME", "Full Time"
        PART_TIME = "PART_TIME", "Part Time"
        CONTRACT = "CONTRACT", "Contract"
        INTERNSHIP = "INTERNSHIP", "Internship"
        FREELANCE = "FREELANCE", "Freelance"

    class WorkMode(models.TextChoices):
        ONSITE = "ONSITE", "Onsite"
        REMOTE = "REMOTE", "Remote"
        HYBRID = "HYBRID", "Hybrid"

    class ExperienceLevel(models.TextChoices):
        ENTRY = "ENTRY", "Entry Level"
        JUNIOR = "JUNIOR", "Junior"
        MID = "MID", "Mid Level"
        SENIOR = "SENIOR", "Senior"
        LEAD = "LEAD", "Lead"
        MANAGER = "MANAGER", "Manager"

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        PUBLISHED = "PUBLISHED", "Published"
        PAUSED = "PAUSED", "Paused"
        CLOSED = "CLOSED", "Closed"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="jobs",
    )
    recruiter = models.ForeignKey(
        RecruiterProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="jobs",
    )
    category = models.ForeignKey(
        JobCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="jobs",
    )
    title = models.CharField(
        max_length=255,
    )
    slug = models.SlugField(
        max_length=300,
        unique=True,
    )
    description = models.TextField()
    responsibilities = models.TextField(
        blank=True,
    )
    requirements = models.TextField(
        blank=True,
    )
    preferred_qualifications = models.TextField(
        blank=True,
    )
    location = models.CharField(
        max_length=255,
        blank=True,
    )
    employment_type = models.CharField(
        max_length=20,
        choices=EmploymentType.choices,
    )
    work_mode = models.CharField(
        max_length=20,
        choices=WorkMode.choices,
    )
    experience_level = models.CharField(
        max_length=20,
        choices=ExperienceLevel.choices,
    )
    minimum_experience = models.PositiveIntegerField(
        default=0,
        help_text="Minimum required experience in years.",
    )
    maximum_experience = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Maximum required experience in years.",
    )
    minimum_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )
    maximum_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )
    salary_currency = models.CharField(
        max_length=10,
        default="INR",
    )
    openings = models.PositiveIntegerField(
        default=1,
    )
    application_deadline = models.DateField(
        null=True,
        blank=True,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    is_featured = models.BooleanField(
        default=False,
    )
    views_count = models.PositiveIntegerField(
        default=0,
    )
    applications_count = models.PositiveIntegerField(
        default=0,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )
    published_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "jobs"
        ordering = ["-created_at"]
        verbose_name = "Job"
        verbose_name_plural = "Jobs"

    def clean(self):
        super().clean()

        if self.recruiter and self.company:
            if self.recruiter.company_id != self.company_id:
                raise ValidationError(
                    {
                        "recruiter": "The recruiter must belong to the selected company."
                    }
                )

        if (
            self.minimum_experience is not None
            and self.maximum_experience is not None
            and self.minimum_experience > self.maximum_experience
        ):
            raise ValidationError(
                {
                    "maximum_experience": "Maximum experience cannot be less than minimum experience."
                }
            )

        if (
            self.minimum_salary is not None
            and self.maximum_salary is not None
            and self.minimum_salary > self.maximum_salary
        ):
            raise ValidationError(
                {
                    "maximum_salary": "Maximum salary cannot be less than minimum salary."
                }
            )

        if self.openings < 1:
            raise ValidationError(
                {"openings": "There must be at least one opening."}
            )

    def __str__(self):
        return f"{self.title} - {self.company.name}"


class JobSkill(models.Model):
    class Importance(models.TextChoices):
        REQUIRED = "REQUIRED", "Required"
        PREFERRED = "PREFERRED", "Preferred"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name="job_skills",
    )
    skill_name = models.CharField(
        max_length=100,
    )
    importance = models.CharField(
        max_length=20,
        choices=Importance.choices,
        default=Importance.REQUIRED,
    )
    minimum_years = models.PositiveIntegerField(
        default=0,
    )

    class Meta:
        db_table = "job_skills"
        unique_together = ("job", "skill_name")
        ordering = ["skill_name"]

    def __str__(self):
        return f"{self.job.title} - {self.skill_name}"
