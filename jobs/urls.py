from django.urls import path

from .views import (
    PublishedJobListView,
    PublishedJobDetailView,
    RecruiterJobCreateView,
    RecruiterJobListView,
    RecruiterJobUpdateView,
    RecruiterJobPublishView,
)

urlpatterns = [
    path(
        "",
        PublishedJobListView.as_view(),
        name="job-list",
    ),
    path(
        "recruiter/",
        RecruiterJobListView.as_view(),
        name="recruiter-job-list",
    ),

    path(
        "recruiter/create/",
        RecruiterJobCreateView.as_view(),
        name="recruiter-job-create",
    ),
    path(
        "recruiter/<uuid:id>/",
        RecruiterJobUpdateView.as_view(),
        name="recruiter-job-update",
    ),
    path(
    "recruiter/<uuid:id>/publish/",
    RecruiterJobPublishView.as_view(),
    name="recruiter-job-publish",
    ),

    path(
        "<uuid:id>/",
        PublishedJobDetailView.as_view(),
        name="job-detail",
    ),
]