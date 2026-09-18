from django.urls import path

from .views import (
    ApplyForJobView,
    MyApplicationsView,
    SaveJobView,
    MySavedJobsView,
    RecruiterApplicationListView,
    RecruiterApplicationDetailView,
)


urlpatterns = [

    # Candidate
    path(
        "apply/",
        ApplyForJobView.as_view(),
        name="apply-job",
    ),

    path(
        "my/",
        MyApplicationsView.as_view(),
        name="my-applications",
    ),

    path(
        "save/",
        SaveJobView.as_view(),
        name="save-job",
    ),

    path(
        "saved/",
        MySavedJobsView.as_view(),
        name="saved-jobs",
    ),

    # Recruiter
    path(
        "recruiter/",
        RecruiterApplicationListView.as_view(),
        name="recruiter-applications",
    ),

    path(
        "recruiter/<uuid:pk>/",
        RecruiterApplicationDetailView.as_view(),
        name="recruiter-application-detail",
    ),
]