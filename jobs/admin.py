from django.contrib import admin

from .models import Job, JobCategory, JobSkill


@admin.register(JobCategory)
class JobCategoryAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "is_active",
        "created_at",
    )

    search_fields = (
        "name",
    )

    list_filter = (
        "is_active",
    )

    ordering = (
        "name",
    )


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "company",
        "recruiter",
        "employment_type",
        "work_mode",
        "experience_level",
        "status",
        "is_featured",
        "created_at",
    )

    search_fields = (
        "title",
        "company__name",
        "recruiter__user__email",
        "location",
    )

    list_filter = (
        "status",
        "employment_type",
        "work_mode",
        "experience_level",
        "is_featured",
        "category",
    )

    prepopulated_fields = {
        "slug": ("title",),
    }

    readonly_fields = (
        "views_count",
        "applications_count",
        "created_at",
        "updated_at",
        "published_at",
    )

    ordering = (
        "-created_at",
    )


@admin.register(JobSkill)
class JobSkillAdmin(admin.ModelAdmin):

    list_display = (
        "job",
        "skill_name",
        "importance",
        "minimum_years",
    )

    search_fields = (
        "skill_name",
        "job__title",
    )

    list_filter = (
        "importance",
    )