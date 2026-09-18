from django.contrib import admin

from .models import Resume


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):

    list_display = (
        "candidate",
        "version",
        "ats_score",
        "uploaded_at",
    )

    search_fields = (
        "candidate__user__email",
        "candidate__user__username",
    )

    list_filter = (
        "uploaded_at",
    )

    readonly_fields = (
        "uploaded_at",
    )

    ordering = (
        "-uploaded_at",
    )