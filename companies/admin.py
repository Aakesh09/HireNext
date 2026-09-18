from django.contrib import admin

from .models import Company


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "industry",
        "company_size",
        "is_verified",
        "created_at",
    )

    search_fields = (
        "name",
        "email",
        "industry",
    )

    list_filter = (
        "industry",
        "company_size",
        "is_verified",
    )

    prepopulated_fields = {
        "slug": ("name",),
    }

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = (
        "name",
    )