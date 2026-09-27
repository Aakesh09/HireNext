from rest_framework import serializers

from .models import Job, JobCategory, JobSkill


class JobCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = JobCategory
        fields = [
            "id",
            "name",
            "description",
            "is_active",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
        ]


class JobSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobSkill
        fields = [
            "id",
            "skill_name",
            "importance",
            "minimum_years",
        ]
        read_only_fields = [
            "id",
        ]


class JobSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(
        source="company.name",
        read_only=True,
    )

    recruiter_name = serializers.SerializerMethodField()

    category_name = serializers.CharField(
        source="category.name",
        read_only=True,
    )

    job_skills = JobSkillSerializer(
        many=True,
        read_only=True,
    )

    employment_type_display = serializers.CharField(
        source="get_employment_type_display",
        read_only=True,
    )

    work_mode_display = serializers.CharField(
        source="get_work_mode_display",
        read_only=True,
    )

    experience_level_display = serializers.CharField(
        source="get_experience_level_display",
        read_only=True,
    )

    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    class Meta:
        model = Job
        fields = [
            "id",
            "company",
            "company_name",
            "recruiter",
            "recruiter_name",
            "category",
            "category_name",
            "title",
            "slug",
            "description",
            "responsibilities",
            "requirements",
            "preferred_qualifications",
            "location",
            "employment_type",
            "employment_type_display",
            "work_mode",
            "work_mode_display",
            "experience_level",
            "experience_level_display",
            "minimum_experience",
            "maximum_experience",
            "minimum_salary",
            "maximum_salary",
            "salary_currency",
            "openings",
            "application_deadline",
            "status",
            "status_display",
            "is_featured",
            "views_count",
            "applications_count",
            "created_at",
            "updated_at",
            "published_at",
            "job_skills",
        ]

        read_only_fields = [
            "id",
            "company_name",
            "recruiter_name",
            "category_name",
            "employment_type_display",
            "work_mode_display",
            "experience_level_display",
            "status_display",
            "views_count",
            "applications_count",
            "created_at",
            "updated_at",
            "published_at",
            "job_skills",
        ]

    def get_recruiter_name(self, obj):
        if not obj.recruiter:
            return None

        return (
            f"{obj.recruiter.user.first_name} "
            f"{obj.recruiter.user.last_name}"
        ).strip()

    def validate(self, attrs):
        company = attrs.get("company")
        recruiter = attrs.get("recruiter")

        if company and recruiter:
            if recruiter.company_id != company.id:
                raise serializers.ValidationError(
                    {
                        "recruiter": (
                            "The recruiter must belong to the selected company."
                        )
                    }
                )

        minimum_experience = attrs.get(
            "minimum_experience",
            self.instance.minimum_experience
            if self.instance
            else 0,
        )

        maximum_experience = attrs.get(
            "maximum_experience",
            self.instance.maximum_experience
            if self.instance
            else None,
        )

        if (
            maximum_experience is not None
            and minimum_experience > maximum_experience
        ):
            raise serializers.ValidationError(
                {
                    "maximum_experience": (
                        "Maximum experience cannot be less "
                        "than minimum experience."
                    )
                }
            )

        minimum_salary = attrs.get(
            "minimum_salary",
            self.instance.minimum_salary
            if self.instance
            else None,
        )

        maximum_salary = attrs.get(
            "maximum_salary",
            self.instance.maximum_salary
            if self.instance
            else None,
        )

        if (
            minimum_salary is not None
            and maximum_salary is not None
            and minimum_salary > maximum_salary
        ):
            raise serializers.ValidationError(
                {
                    "maximum_salary": (
                        "Maximum salary cannot be less "
                        "than minimum salary."
                    )
                }
            )

        openings = attrs.get(
            "openings",
            self.instance.openings
            if self.instance
            else 1,
        )

        if openings < 1:
            raise serializers.ValidationError(
                {
                    "openings": "There must be at least one opening."
                }
            )

        return attrs
class RecruiterJobCreateSerializer(serializers.ModelSerializer):
        class Meta:
            model = Job
            fields = [
                "id",
                "company",
                "recruiter",
                "category",
                "title",
                "slug",
                "description",
                "responsibilities",
                "requirements",
                "preferred_qualifications",
                "location",
                "employment_type",
                "work_mode",
                "experience_level",
                "minimum_experience",
                "maximum_experience",
                "minimum_salary",
                "maximum_salary",
                "salary_currency",
                "openings",
                "application_deadline",
                "status",
                "is_featured",
                "created_at",
                "updated_at",
                "published_at",
            ]

            read_only_fields = [
                "id",
                "recruiter",
                "created_at",
                "updated_at",
                "published_at",
            ]

        def validate_company(self, value):
            request = self.context["request"]
            recruiter = request.user.recruiter_profile

            if value.id != recruiter.company_id:
                raise serializers.ValidationError(
                    "You can only create jobs for your own company."
                )

            return value

        def validate_status(self, value):
            if value != Job.Status.DRAFT:
                raise serializers.ValidationError(
                    "New jobs must be created as DRAFT."
                )

            return value

        def create(self, validated_data):
            request = self.context["request"]
            recruiter = request.user.recruiter_profile

            validated_data["recruiter"] = recruiter
            validated_data["status"] = Job.Status.DRAFT

            job = Job(**validated_data)
            job.full_clean()
            job.save()

            return job