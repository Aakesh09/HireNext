from django.db import IntegrityError, transaction
from django.db.models import Q,Count
from rest_framework import generics, serializers,filters
from rest_framework.response import Response
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
    """
    Candidate applies for a published job.
    """

    serializer_class = JobApplicationSerializer
    permission_classes = [IsCandidateRole]

    def perform_create(self, serializer):
        candidate = self.request.user.candidate_profile

        try:
            with transaction.atomic():

                application = serializer.save(
                    candidate=candidate
                )

                job = application.job

                job.applications_count += 1

                job.save(
                    update_fields=[
                        "applications_count",
                    ]
                )

                create_application_received_notification(
                    application
                )

        except IntegrityError:

            raise serializers.ValidationError(
                {
                    "job": (
                        "You have already applied "
                        "for this job."
                    )
                }
                )

class MyApplicationsView(generics.ListAPIView):
    """
    Returns applications created by
    the logged-in candidate.
    """

    serializer_class = JobApplicationSerializer
    permission_classes = [IsCandidateRole]

    def get_queryset(self):

        return (
            JobApplication.objects
            .filter(
                candidate=self.request.user.candidate_profile
            )
            .select_related(
                "job",
                "job__company",
                "job__recruiter__user",
                "resume",
            )
        )

class MyApplicationDetailView(generics.RetrieveAPIView):
    """
    Candidate can view one of their own applications.
    """

    serializer_class = JobApplicationSerializer
    permission_classes = [IsCandidateRole]

    def get_queryset(self):
        return (
            JobApplication.objects
            .filter(
                candidate=self.request.user.candidate_profile
            )
            .select_related(
                "job",
                "job__company",
                "job__recruiter__user",
                "resume",
            )
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
    Returns saved jobs of the
    logged-in candidate.
    """

    serializer_class = SavedJobSerializer
    permission_classes = [IsCandidateRole]

    def get_queryset(self):

        return (
            SavedJob.objects
            .filter(
                candidate=self.request.user.candidate_profile
            )
            .select_related(
                "job",
                "job__company",
            )
        )


class RecruiterApplicationListView(generics.ListAPIView):
    """
    Recruiter can view applications for jobs
    belonging to their company.

    Supports:
    - Filter by application status
    - Filter by job
    - Search by candidate name
    - Search by candidate email
    - Search by job title
    - Ordering
    - Pagination
    """

    serializer_class = RecruiterApplicationSerializer

    permission_classes = [IsRecruiterRole]

    filter_backends = [
        filters.OrderingFilter,
    ]

    ordering_fields = [
        "applied_at",
        "updated_at",
        "status",
        "job__title",
        "ats_score",
    ]

    ordering = [
        "-applied_at",
    ]

    def get_queryset(self):
        recruiter = self.request.user.recruiter_profile

        queryset = (
            JobApplication.objects.filter(
                job__company=recruiter.company
            )
            .select_related(
                "candidate",
                "candidate__user",
                "job",
                "job__company",
                "resume",
            )
        )

        # Filter by application status
        status = self.request.query_params.get("status")

        if status:
            queryset = queryset.filter(
                status=status
            )

        # Filter by specific job
        job = self.request.query_params.get("job")

        if job:
            queryset = queryset.filter(
                job_id=job
            )
        # Filter by minimum ATS score
        min_ats_score = self.request.query_params.get(
            "min_ats_score"
        )

        if min_ats_score:
            try:
                queryset = queryset.filter(
                    ats_score__gte=float(min_ats_score)
                )
            except ValueError:
                pass


        # Filter by maximum ATS score
        max_ats_score = self.request.query_params.get(
            "max_ats_score"
        )

        if max_ats_score:
            try:
                queryset = queryset.filter(
                    ats_score__lte=float(max_ats_score)
                )
            except ValueError:
                pass

        # Search
        search = self.request.query_params.get("search")

        if search:
            queryset = queryset.filter(
                Q(
                    candidate__user__first_name__icontains=search
                )
                | Q(
                    candidate__user__last_name__icontains=search
                )
                | Q(
                    candidate__user__email__icontains=search
                )
                | Q(
                    job__title__icontains=search
                )
            )

        return queryset

class RecruiterApplicationStatsView(generics.GenericAPIView):
    """
    Recruiter application statistics for their company.
    """

    permission_classes = [IsRecruiterRole]

    def get(self, request, *args, **kwargs):

        recruiter = request.user.recruiter_profile

        queryset = JobApplication.objects.filter(
            job__company=recruiter.company
        )

        # ---------------------------------
        # Statistics for each job
        # ---------------------------------

        jobs = (
            queryset
            .values(
                "job_id",
                "job__title",
            )
            .annotate(
                applications_count=Count("id"),

                applied=Count(
                    "id",
                    filter=Q(
                        status=JobApplication.Status.APPLIED
                    ),
                ),

                reviewing=Count(
                    "id",
                    filter=Q(
                        status=JobApplication.Status.REVIEWING
                    ),
                ),

                shortlisted=Count(
                    "id",
                    filter=Q(
                        status=JobApplication.Status.SHORTLISTED
                    ),
                ),

                interview=Count(
                    "id",
                    filter=Q(
                        status=JobApplication.Status.INTERVIEW
                    ),
                ),

                selected=Count(
                    "id",
                    filter=Q(
                        status=JobApplication.Status.SELECTED
                    ),
                ),

                rejected=Count(
                    "id",
                    filter=Q(
                        status=JobApplication.Status.REJECTED
                    ),
                ),

                withdrawn=Count(
                    "id",
                    filter=Q(
                        status=JobApplication.Status.WITHDRAWN
                    ),
                ),
            )
            .order_by("-applications_count")
        )

        # ---------------------------------
        # Five most recent applications
        # ---------------------------------

        recent_applications = (
            queryset
            .select_related(
                "candidate",
                "candidate__user",
                "job",
                "job__company",
                "resume",
            )
            .order_by("-applied_at")[:5]
        )

        # ---------------------------------
        # Response
        # ---------------------------------

        return Response(
            {
                "total": queryset.count(),

                "applied": queryset.filter(
                    status=JobApplication.Status.APPLIED
                ).count(),

                "reviewing": queryset.filter(
                    status=JobApplication.Status.REVIEWING
                ).count(),

                "shortlisted": queryset.filter(
                    status=JobApplication.Status.SHORTLISTED
                ).count(),

                "interview": queryset.filter(
                    status=JobApplication.Status.INTERVIEW
                ).count(),

                "selected": queryset.filter(
                    status=JobApplication.Status.SELECTED
                ).count(),

                "rejected": queryset.filter(
                    status=JobApplication.Status.REJECTED
                ).count(),

                "withdrawn": queryset.filter(
                    status=JobApplication.Status.WITHDRAWN
                ).count(),

                "jobs": [
                    {
                        "job_id": job["job_id"],
                        "job_title": job["job__title"],
                        "applications": job["applications_count"],
                        "applied": job["applied"],
                        "reviewing": job["reviewing"],
                        "shortlisted": job["shortlisted"],
                        "interview": job["interview"],
                        "selected": job["selected"],
                        "rejected": job["rejected"],
                        "withdrawn": job["withdrawn"],
                    }
                    for job in jobs
                ],

                "recent_applications": [
                    {
                        "id": application.id,
                        "candidate_name": (
                            f"{application.candidate.user.first_name} "
                            f"{application.candidate.user.last_name}"
                        ).strip(),
                        "candidate_email": (
                            application.candidate.user.email
                        ),
                        "job_id": application.job_id,
                        "job_title": application.job.title,
                        "status": application.status,
                        "applied_at": application.applied_at,
                    }
                    for application in recent_applications
                ],
            }
        )

class RecruiterApplicationDetailView(
    generics.RetrieveUpdateAPIView
):
    serializer_class = RecruiterApplicationSerializer
    permission_classes = [IsRecruiterRole]

    def get_queryset(self):
        recruiter = self.request.user.recruiter_profile

        return (
            JobApplication.objects
            .filter(job__company=recruiter.company)
            .select_related(
                "candidate",
                "candidate__user",
                "job",
                "job__company",
                "resume",
            )
        )

    def perform_update(self, serializer):
        application = self.get_object()
        old_status = application.status

        updated_application = serializer.save()

        if old_status != updated_application.status:
            create_application_status_notification(
                updated_application
            )


class WithdrawApplicationView(generics.UpdateAPIView):
    """
    Allow a candidate to withdraw their own application.
    """

    serializer_class = JobApplicationSerializer
    permission_classes = [IsCandidateRole]
    http_method_names = ["patch"]

    def get_queryset(self):
        return (
            JobApplication.objects
            .filter(
                candidate=self.request.user.candidate_profile
            )
            .select_related("job")
        )

    def partial_update(self, request, *args, **kwargs):

        with transaction.atomic():

            application = self.get_object()

            # Already completed applications cannot be withdrawn.
            if application.status in [
                JobApplication.Status.SELECTED,
                JobApplication.Status.REJECTED,
                JobApplication.Status.WITHDRAWN,
            ]:
                return Response(
                    {
                        "detail": (
                            f"Applications with status "
                            f"{application.status} "
                            f"cannot be withdrawn."
                        )
                    },
                    status=400,
                )

            application.status = JobApplication.Status.WITHDRAWN

            application.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )

            job = application.job

            if job.applications_count > 0:
                job.applications_count -= 1

                job.save(
                    update_fields=[
                        "applications_count",
                    ]
                )

            serializer = self.get_serializer(application)

            return Response(
                serializer.data,
                status=200,
            )