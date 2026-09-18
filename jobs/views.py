from django.db.models import Q
from rest_framework import generics
from rest_framework.permissions import AllowAny

from .models import Job
from .serializers import JobSerializer


class PublishedJobListView(generics.ListAPIView):
    """
    List all published jobs.

    Supports:
    - Search by title, description, company, or location
    - Filter by employment type
    - Filter by work mode
    - Filter by experience level
    - Filter by location
    """

    serializer_class = JobSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = (
            Job.objects.filter(
                status=Job.Status.PUBLISHED
            )
            .select_related(
                "company",
                "recruiter__user",
                "category",
            )
            .prefetch_related("job_skills")
        )

        search = self.request.query_params.get("search")
        employment_type = self.request.query_params.get("employment_type")
        work_mode = self.request.query_params.get("work_mode")
        experience_level = self.request.query_params.get("experience_level")
        location = self.request.query_params.get("location")

        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(description__icontains=search)
                | Q(company__name__icontains=search)
                | Q(location__icontains=search)
            )

        if employment_type:
            queryset = queryset.filter(
                employment_type=employment_type
            )

        if work_mode:
            queryset = queryset.filter(
                work_mode=work_mode
            )

        if experience_level:
            queryset = queryset.filter(
                experience_level=experience_level
            )

        if location:
            queryset = queryset.filter(
                location__icontains=location
            )

        return queryset


class PublishedJobDetailView(generics.RetrieveAPIView):
    """
    Retrieve a single published job.
    """

    serializer_class = JobSerializer
    permission_classes = [AllowAny]
    lookup_field = "id"

    def get_queryset(self):
        return (
            Job.objects.filter(
                status=Job.Status.PUBLISHED
            )
            .select_related(
                "company",
                "recruiter__user",
                "category",
            )
            .prefetch_related("job_skills")
        )