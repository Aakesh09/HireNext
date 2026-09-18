from django.db import IntegrityError,transaction
from rest_framework import generics,serializers

from .models import JobApplication, SavedJob

from .serializers import (
    JobApplicationSerializer,
    SavedJobSerializer,
    RecruiterApplicationSerializer,
)

from accounts.permissions import (
    IsCandidateRole,
    IsRecruiterRole,
)
from notifications.services import (
    create_application_received_notification,
    create_application_status_notification,
)

class ApplyForJobView(generics.CreateAPIView):
    serializer_class = JobApplicationSerializer
    permission_classes = [IsCandidateRole]

    def perform_create(self, serializer):
        candidate = self.request.user.candidate_profile

        try:
            with transaction.atomic():
                application = serializer.save(candidate=candidate)

                job = application.job
                job.applications_count += 1
                job.save(update_fields=["applications_count"])

                create_application_received_notification(application)
        except IntegrityError:
            raise serializers.ValidationError({
                "job": "You have already applied for this job."
            })

class MyApplicationsView(generics.ListAPIView):
    """
    Returns applications created by the logged-in candidate.
    """

    serializer_class = JobApplicationSerializer
    permission_classes = [IsCandidateRole]

    def get_queryset(self):
        return JobApplication.objects.filter(
            candidate=self.request.user.candidate_profile
        ).select_related(
            "job",
            "job__company",
            "resume",
        )


class SaveJobView(generics.CreateAPIView):
    """
    Candidate saves a job.
    """

    serializer_class = SavedJobSerializer
    permission_classes = [IsCandidateRole]

    def perform_create(self, serializer):
        serializer.save(
            candidate=self.request.user.candidate_profile
        )


class MySavedJobsView(generics.ListAPIView):
    """
    Returns saved jobs of the logged-in candidate.
    """

    serializer_class = SavedJobSerializer
    permission_classes = [IsCandidateRole]

    def get_queryset(self):
        return SavedJob.objects.filter(
            candidate=self.request.user.candidate_profile
        ).select_related(
            "job",
            "job__company",
        )
class RecruiterApplicationListView(generics.ListAPIView):
    """
    Recruiter can view applications for jobs
    belonging to their company.
    """

    serializer_class = RecruiterApplicationSerializer
    permission_classes = [IsRecruiterRole]

    def get_queryset(self):
        recruiter = self.request.user.recruiter_profile

        return JobApplication.objects.filter(
            job__company=recruiter.company
        ).select_related(
            "candidate",
            "candidate__user",
            "job",
            "job__company",
            "resume",
        )
class RecruiterApplicationDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = RecruiterApplicationSerializer
    permission_classes = [IsRecruiterRole]

    def get_queryset(self):
        recruiter = self.request.user.recruiter_profile

        return JobApplication.objects.filter(
            job__company=recruiter.company
        ).select_related(
            "candidate",
            "candidate__user",
            "job",
            "job__company",
            "resume",
        )

    def perform_update(self, serializer):
        application = self.get_object()

        old_status = application.status

        updated_application = serializer.save()

        new_status = updated_application.status

        if old_status != new_status:
            create_application_status_notification(
                updated_application
            )