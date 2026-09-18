import uuid

from django.conf import settings
from django.db import models


class CandidateProfile(models.Model):

    class Availability(models.TextChoices):
        IMMEDIATELY = "IMMEDIATELY", "Immediately"
        FIFTEEN_DAYS = "15_DAYS", "15 Days"
        THIRTY_DAYS = "30_DAYS", "30 Days"
        SIXTY_DAYS = "60_DAYS", "60 Days"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="candidate_profile",
    )

    headline = models.CharField(max_length=200)

    about = models.TextField(blank=True)

    current_location = models.CharField(
        max_length=100,
        blank=True,
    )

    github_url = models.URLField(blank=True)

    linkedin_url = models.URLField(blank=True)

    portfolio_url = models.URLField(blank=True)

    current_job_title = models.CharField(
        max_length=100,
        blank=True,
    )

    current_company = models.CharField(
        max_length=100,
        blank=True,
    )

    years_of_experience = models.PositiveIntegerField(default=0)

    expected_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    availability = models.CharField(
        max_length=20,
        choices=Availability.choices,
        default=Availability.IMMEDIATELY,
    )

    profile_completion = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "candidate_profiles"
        ordering = ["-created_at"]

    def __str__(self):
        return self.user.email


class Education(models.Model):

    class EducationLevel(models.TextChoices):
        HIGH_SCHOOL = "HIGH_SCHOOL", "High School"
        DIPLOMA = "DIPLOMA", "Diploma"
        BACHELOR = "BACHELOR", "Bachelor"
        MASTER = "MASTER", "Master"
        PHD = "PHD", "PhD"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    candidate = models.ForeignKey(
        CandidateProfile,
        on_delete=models.CASCADE,
        related_name="educations",
    )

    education_level = models.CharField(
        max_length=20,
        choices=EducationLevel.choices,
    )

    degree = models.CharField(max_length=150)

    specialization = models.CharField(
        max_length=150,
        blank=True,
    )

    institution = models.CharField(max_length=255)

    board_or_university = models.CharField(max_length=255)

    start_date = models.DateField()

    end_date = models.DateField(
        blank=True,
        null=True,
    )

    currently_studying = models.BooleanField(default=False)

    grade = models.CharField(
        max_length=50,
        blank=True,
    )

    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-end_date", "-start_date"]

    def __str__(self):
        return f"{self.degree} - {self.institution}"


class Experience(models.Model):

    class EmploymentType(models.TextChoices):
        FULL_TIME = "FULL_TIME", "Full Time"
        PART_TIME = "PART_TIME", "Part Time"
        INTERNSHIP = "INTERNSHIP", "Internship"
        FREELANCE = "FREELANCE", "Freelance"
        CONTRACT = "CONTRACT", "Contract"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    candidate = models.ForeignKey(
        CandidateProfile,
        on_delete=models.CASCADE,
        related_name="experiences",
    )

    company_name = models.CharField(max_length=255)

    job_title = models.CharField(max_length=255)

    employment_type = models.CharField(
        max_length=20,
        choices=EmploymentType.choices,
    )

    location = models.CharField(
        max_length=150,
        blank=True,
    )

    currently_working = models.BooleanField(default=False)

    start_date = models.DateField()

    end_date = models.DateField(
        blank=True,
        null=True,
    )

    description = models.TextField()

    technologies = models.CharField(
        max_length=500,
        blank=True,
        help_text="Comma separated technologies",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
            ordering = ["-start_date"]
    
    def __str__(self):
            return f"{self.job_title} - {self.company_name}"
class Skill(models.Model):

    class Category(models.TextChoices):
        PROGRAMMING = "PROGRAMMING", "Programming"
        DATABASE = "DATABASE", "Database"
        CLOUD = "CLOUD", "Cloud"
        DEVOPS = "DEVOPS", "DevOps"
        FRAMEWORK = "FRAMEWORK", "Framework"
        TOOL = "TOOL", "Tool"
        SOFT_SKILL = "SOFT_SKILL", "Soft Skill"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    name = models.CharField(
        max_length=100,
        unique=True,
    )

    category = models.CharField(
        max_length=30,
        choices=Category.choices,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
class CandidateSkill(models.Model):

    class Level(models.TextChoices):
        BEGINNER = "BEGINNER", "Beginner"
        INTERMEDIATE = "INTERMEDIATE", "Intermediate"
        ADVANCED = "ADVANCED", "Advanced"
        EXPERT = "EXPERT", "Expert"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    candidate = models.ForeignKey(
        CandidateProfile,
        on_delete=models.CASCADE,
        related_name="skills",
    )

    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
    )

    proficiency = models.CharField(
        max_length=20,
        choices=Level.choices,
    )

    years_of_experience = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("candidate", "skill")

    def __str__(self):
        return f"{self.candidate.user.email} - {self.skill.name}"

class Project(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    candidate = models.ForeignKey(
        CandidateProfile,
        on_delete=models.CASCADE,
        related_name="projects",
    )

    title = models.CharField(max_length=200)

    description = models.TextField()

    github_url = models.URLField(blank=True)

    live_url = models.URLField(blank=True)

    technologies = models.CharField(
        max_length=500,
        blank=True,
    )

    start_date = models.DateField()

    end_date = models.DateField(
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
class Certification(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    candidate = models.ForeignKey(
        CandidateProfile,
        on_delete=models.CASCADE,
        related_name="certifications",
    )

    title = models.CharField(max_length=255)

    issuing_organization = models.CharField(max_length=255)

    issue_date = models.DateField()

    expiry_date = models.DateField(
        blank=True,
        null=True,
    )

    credential_id = models.CharField(
        max_length=150,
        blank=True,
    )

    credential_url = models.URLField(blank=True)

    class Meta:
        ordering = ["-issue_date"]

    def __str__(self):
        return self.title
