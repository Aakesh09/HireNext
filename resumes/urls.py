from django.urls import path

from .views import (
    ResumeUploadView,
    MyResumesView,
    ResumeDetailView,
)


urlpatterns = [
    path(
        "",
        ResumeUploadView.as_view(),
        name="resume-upload",
    ),

    path(
        "my/",
        MyResumesView.as_view(),
        name="my-resumes",
    ),
    path(
        "<uuid:pk>/",
        ResumeDetailView.as_view(),
        name="resume-details",
    ),
]