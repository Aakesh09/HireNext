import uuid

from django.db import models


class Resume(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    candidate = models.ForeignKey(
        "candidates.CandidateProfile",
        on_delete=models.CASCADE,
        related_name="resumes",
    )

    resume_file = models.FileField(
        upload_to="resumes/",
    )

    version = models.PositiveIntegerField(
        default=1,
    )

    ats_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
    )

    parsed_text = models.TextField(
        blank=True,
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        db_table = "resumes"
        ordering = ["-uploaded_at"]
        verbose_name = "Resume"
        verbose_name_plural = "Resumes"

    def __str__(self):
        return (
            f"{self.candidate.user.email} "
            f"Resume v{self.version}"
        )