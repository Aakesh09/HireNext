from django.db import transaction

from rest_framework import generics

from accounts.permissions import IsCandidateRole

from .models import Resume
from .serializers import ResumeSerializer
from .services import extract_text_from_pdf


class ResumeUploadView(generics.CreateAPIView):
    """
    Candidate uploads a resume.
    """

    serializer_class = ResumeSerializer
    permission_classes = [IsCandidateRole]

    def perform_create(self, serializer):

        candidate = self.request.user.candidate_profile

        with transaction.atomic():

            last_resume = (
                Resume.objects
                .filter(candidate=candidate)
                .order_by("-version")
                .first()
            )

            if last_resume:
                next_version = last_resume.version + 1
            else:
                next_version = 1

            resume = serializer.save(
                candidate=candidate,
                version=next_version,
            )

            # Extract text from uploaded PDF
            parsed_text = extract_text_from_pdf(
                resume.resume_file
            )

            resume.parsed_text = parsed_text

            resume.save(
                update_fields=["parsed_text"]
            )


class MyResumesView(generics.ListAPIView):
    """
    Returns resumes belonging to
    the logged-in candidate,
    ordered by the latest version first.
    """

    serializer_class = ResumeSerializer
    permission_classes = [IsCandidateRole]

    def get_queryset(self):

        return (
            Resume.objects
            .filter(
                candidate=self.request.user.candidate_profile
            )
            .order_by("-version")
        )


class ResumeDetailView(generics.RetrieveDestroyAPIView):
    """
    Candidate can view or delete
    one of their own resumes.
    """

    serializer_class = ResumeSerializer
    permission_classes = [IsCandidateRole]

    def get_queryset(self):

        return (
            Resume.objects
            .filter(
                candidate=self.request.user.candidate_profile
            )
        )