from django.utils import timezone
from rest_framework import serializers

from .models import JobApplication, SavedJob


class JobApplicationSerializer(serializers.ModelSerializer):

    candidate_email = serializers.EmailField(
        source="candidate.user.email",
        read_only=True,
    )

    job_title = serializers.CharField(
        source="job.title",
        read_only=True,
    )

    company_name = serializers.CharField(
        source="job.company.name",
        read_only=True,
    )

    resume_version = serializers.IntegerField(
        read_only=True,
    )

    class Meta:
        model = JobApplication

        fields = [
            "id",
            "candidate",
            "candidate_email",
            "job",
            "job_title",
            "company_name",
            "resume",
            "resume_version",
            "cover_letter",
            "status",
            "ats_score",
            "matched_required_skills",
            "missing_required_skills",
            "matched_preferred_skills",
            "missing_preferred_skills",
            "applied_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "candidate",
            "candidate_email",
            "job_title",
            "company_name",
            "resume_version",
            "status",
            "ats_score",
            "matched_required_skills",
            "missing_required_skills",
            "matched_preferred_skills",
            "missing_preferred_skills",
            "applied_at",
            "updated_at",
        ]

    def validate(self, attrs):

        request = self.context["request"]

        candidate = request.user.candidate_profile
        job = attrs["job"]
        resume = attrs.get("resume")

        # 1. Job must be published
        if job.status != "PUBLISHED":
            raise serializers.ValidationError(
                {
                    "job": (
                        "Candidates can only apply "
                        "to published jobs."
                    )
                }
            )

        # 2. Candidate cannot apply twice
        if JobApplication.objects.filter(
            candidate=candidate,
            job=job,
        ).exists():
            raise serializers.ValidationError(
                {
                    "job": (
                        "You have already applied "
                        "for this job."
                    )
                }
            )

        # 3. Check job openings
        if job.applications_count >= job.openings:
            raise serializers.ValidationError(
                {
                    "job": (
                        "All available positions for "
                        "this job have been filled."
                    )
                }
            )

        # 4. Check application deadline
        if (
            job.application_deadline
            and job.application_deadline < timezone.now().date()
        ):
            raise serializers.ValidationError({
                "job": "The application deadline has passed."
            })

        # 5. Resume must belong to candidate
        if resume and resume.candidate_id != candidate.id:
            raise serializers.ValidationError(
                {
                    "resume": (
                        "You can only use "
                        "your own resume."
                    )
                }
            )

        return attrs

    def create(self, validated_data):

        request = self.context["request"]

        candidate = request.user.candidate_profile

        job = validated_data["job"]
        resume = validated_data.get("resume")

        ats_result = {
            "score": 0,
            "matched_required": [],
            "missing_required": [],
            "matched_preferred": [],
            "missing_preferred": [],
        }

        if resume and resume.parsed_text:
            from resumes.services import calculate_ats_score

            ats_result = calculate_ats_score(
                resume.parsed_text,
                job.requirements,
                job.preferred_qualifications,
            )

        application = JobApplication.objects.create(
            candidate=candidate,
            job=job,
            resume=resume,
            resume_version=resume.version if resume else None,
            cover_letter=validated_data.get("cover_letter", ""),
            ats_score=ats_result["score"],
            matched_required_skills=ats_result["matched_required"],
            missing_required_skills=ats_result["missing_required"],
            matched_preferred_skills=ats_result["matched_preferred"],
            missing_preferred_skills=ats_result["missing_preferred"],
        )

        return application


class SavedJobSerializer(serializers.ModelSerializer):

    job_title = serializers.CharField(
        source="job.title",
        read_only=True,
    )

    company_name = serializers.CharField(
        source="job.company.name",
        read_only=True,
    )

    class Meta:
        model = SavedJob

        fields = [
            "id",
            "candidate",
            "job",
            "job_title",
            "company_name",
            "saved_at",
        ]

        read_only_fields = [
            "id",
            "candidate",
            "job_title",
            "company_name",
            "saved_at",
        ]

    def validate_job(self, value):

        request = self.context["request"]

        candidate = request.user.candidate_profile

        if SavedJob.objects.filter(
            candidate=candidate,
            job=value,
        ).exists():
            raise serializers.ValidationError(
                "You have already saved this job."
            )

        return value

    def create(self, validated_data):

        request = self.context["request"]

        candidate = request.user.candidate_profile

        return SavedJob.objects.create(
            candidate=candidate,
            **validated_data,
        )


class RecruiterApplicationSerializer(serializers.ModelSerializer):

    candidate_name = serializers.SerializerMethodField()

    candidate_email = serializers.EmailField(
        source="candidate.user.email",
        read_only=True,
    )

    job_title = serializers.CharField(
        source="job.title",
        read_only=True,
    )

    company_name = serializers.CharField(
        source="job.company.name",
        read_only=True,
    )

    resume_version = serializers.IntegerField(
        read_only=True,
    )

    class Meta:
        model = JobApplication

        fields = [
            "id",
            "candidate",
            "candidate_name",
            "candidate_email",
            "job",
            "job_title",
            "company_name",
            "resume",
            "resume_version",
            "cover_letter",
            "status",
            "recruiter_notes",
            "ats_score",
            "matched_required_skills",
            "missing_required_skills",
            "matched_preferred_skills",
            "missing_preferred_skills",
            "applied_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "candidate",
            "candidate_name",
            "candidate_email",
            "job",
            "job_title",
            "company_name",
            "resume",
            "resume_version",
            "cover_letter",
            "ats_score",
            "matched_required_skills",
            "missing_required_skills",
            "matched_preferred_skills",
            "missing_preferred_skills",
            "applied_at",
            "updated_at",
        ]

    def get_candidate_name(self, obj):
        return (
            f"{obj.candidate.user.first_name} "
            f"{obj.candidate.user.last_name}"
        ).strip()

    def validate_status(self, value):
        """
        Validate recruiter application status transitions.
        """

        application = self.instance

        # Creating an application through this serializer
        # is not expected, but keep validation safe.
        if not application:
            return value

        current_status = application.status

        allowed_transitions = {
            JobApplication.Status.APPLIED: [
                JobApplication.Status.REVIEWING,
                JobApplication.Status.REJECTED,
            ],

            JobApplication.Status.REVIEWING: [
                JobApplication.Status.SHORTLISTED,
                JobApplication.Status.REJECTED,
            ],

            JobApplication.Status.SHORTLISTED: [
                JobApplication.Status.INTERVIEW,
                JobApplication.Status.REJECTED,
            ],

            JobApplication.Status.INTERVIEW: [
                JobApplication.Status.SELECTED,
                JobApplication.Status.REJECTED,
            ],

            JobApplication.Status.SELECTED: [],

            JobApplication.Status.REJECTED: [],

            JobApplication.Status.WITHDRAWN: [],
        }

        # Same status is allowed.
        if value == current_status:
            return value

        if value not in allowed_transitions.get(
            current_status,
            [],
        ):
            raise serializers.ValidationError(
                f"Cannot change application status "
                f"from {current_status} to {value}."
            )

        return value