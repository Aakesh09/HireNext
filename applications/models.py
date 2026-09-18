import uuid

from django.core.exceptions import ValidationError
from django.db import models


class JobApplication(models.Model):

    class Status(models.TextChoices):
        APPLIED = "APPLIED", "Applied"
        REVIEWING = "REVIEWING", "Reviewing"
        SHORTLISTED = "SHORTLISTED", "Shortlisted"
        INTERVIEW = "INTERVIEW", "Interview"
        SELECTED = "SELECTED", "Selected"
        REJECTED = "REJECTED", "Rejected"
        WITHDRAWN = "WITHDRAWN", "Withdrawn"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    candidate = models.ForeignKey(
        "candidates.CandidateProfile",
        on_delete=models.CASCADE,
        related_name="applications",
    )

    job = models.ForeignKey(
        "jobs.Job",
        on_delete=models.CASCADE,
        related_name="applications",
    )

    resume = models.ForeignKey(
        "resumes.Resume",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="applications",
    )

    cover_letter = models.TextField(
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.APPLIED,
    )

    recruiter_notes = models.TextField(
        blank=True,
    )

    applied_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        db_table = "job_applications"
        ordering = ["-applied_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["candidate", "job"],
                name="unique_candidate_job_application",
            )
        ]

    def clean(self):
        super().clean()

        if self.candidate_id and self.job_id:

            if self.job.status != "PUBLISHED":
                raise ValidationError(
                    {
                        "job": (
                            "Candidates can only apply "
                            "to published jobs."
                        )
                    }
                )

        if self.resume_id:

            if self.resume.candidate_id != self.candidate_id:
                raise ValidationError(
                    {
                        "resume": (
                            "The selected resume must "
                            "belong to the candidate."
                        )
                    }
                )

    def __str__(self):
        return (
            f"{self.candidate.user.email} → "
            f"{self.job.title} ({self.status})"
        )


class SavedJob(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    candidate = models.ForeignKey(
        "candidates.CandidateProfile",
        on_delete=models.CASCADE,
        related_name="saved_jobs",
    )

    job = models.ForeignKey(
        "jobs.Job",
        on_delete=models.CASCADE,
        related_name="saved_by",
    )

    saved_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        db_table = "saved_jobs"
        ordering = ["-saved_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["candidate", "job"],
                name="unique_candidate_saved_job",
            )
        ]

    def __str__(self):
        return (
            f"{self.candidate.user.email} "
            f"saved {self.job.title}"
        )