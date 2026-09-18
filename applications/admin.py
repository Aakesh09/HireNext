from django.contrib import admin

from .models import JobApplication, SavedJob


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):

    list_display = (
        "candidate",
        "job",
        "status",
        "applied_at",
        "updated_at",
    )

    search_fields = (
        "candidate__user__email",
        "candidate__user__username",
        "job__title",
        "job__company__name",
    )

    list_filter = (
        "status",
        "applied_at",
    )

    readonly_fields = (
        "applied_at",
        "updated_at",
    )

    ordering = (
        "-applied_at",
    )


@admin.register(SavedJob)
class SavedJobAdmin(admin.ModelAdmin):

    list_display = (
        "candidate",
        "job",
        "saved_at",
    )

    search_fields = (
        "candidate__user__email",
        "job__title",
    )

    readonly_fields = (
        "saved_at",
    )

    ordering = (
        "-saved_at",
    )