from django.urls import path

from .views import (
    PublishedJobListView,
    PublishedJobDetailView,
)

urlpatterns = [
    path("", PublishedJobListView.as_view(), name="job-list"),
    path("<uuid:id>/", PublishedJobDetailView.as_view(), name="job-detail"),
]