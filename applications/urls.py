from django.urls import path

from .views import (
    ApplyForJobView,
    MyApplicationsView,
    SaveJobView,
    MySavedJobsView,
    RecruiterApplicationListView,
    RecruiterApplicationDetailView,
    RecruiterApplicationStatsView,
    WithdrawApplicationView,
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
        "my/<uuid:pk>/withdraw/",
        WithdrawApplicationView.as_view(),
        name="withdraw-application",
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
    "recruiter/stats/",
    RecruiterApplicationStatsView.as_view(),
    name="recruiter-application-stats",
    ),

    path(
        "recruiter/<uuid:pk>/",
        RecruiterApplicationDetailView.as_view(),
        name="recruiter-application-detail",
    ),
]