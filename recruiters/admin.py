from django.contrib import admin

from .models import RecruiterProfile


@admin.register(RecruiterProfile)
class RecruiterProfileAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "company",
        "designation",
        "department",
        "is_primary_recruiter",
        "created_at",
    )

    search_fields = (
        "user__email",
        "user__username",
        "company__name",
        "designation",
        "department",
        "employee_id",
    )

    list_filter = (
        "company",
        "department",
        "is_primary_recruiter",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = (
        "-created_at",
    )