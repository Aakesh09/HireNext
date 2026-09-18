from django.contrib import admin

from .models import (
    CandidateProfile,
    Education,
    Experience,
    Skill,
    CandidateSkill,
    Project,
    Certification,
)


@admin.register(CandidateProfile)
class CandidateProfileAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "headline",
        "current_location",
        "availability",
        "profile_completion",
    )

    search_fields = (
        "user__email",
        "headline",
    )

    list_filter = (
        "availability",
    )

    ordering = (
        "-created_at",
    )


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):

    list_display = (
        "candidate",
        "education_level",
        "degree",
        "institution",
        "currently_studying",
    )

    search_fields = (
        "degree",
        "institution",
    )

    list_filter = (
        "education_level",
        "currently_studying",
    )

    ordering = (
        "-start_date",
    )


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):

    list_display = (
        "candidate",
        "company_name",
        "job_title",
        "employment_type",
        "currently_working",
    )

    search_fields = (
        "company_name",
        "job_title",
    )

    list_filter = (
        "employment_type",
        "currently_working",
    )

    ordering = (
        "-start_date",
    )
@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "category",
    )

    search_fields = (
        "name",
    )

    list_filter = (
        "category",
    )


@admin.register(CandidateSkill)
class CandidateSkillAdmin(admin.ModelAdmin):

    list_display = (
        "candidate",
        "skill",
        "proficiency",
        "years_of_experience",
    )

    list_filter = (
        "proficiency",
    )


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "candidate",
        "start_date",
    )

    search_fields = (
        "title",
    )


@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "candidate",
        "issuing_organization",
        "issue_date",
    )

