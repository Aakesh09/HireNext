from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("admin/", admin.site.urls),


    path(
            "api/jobs/",
            include("jobs.urls"),
        ),

    path(
        "api/applications/",
        include("applications.urls"),
    ),

    path(
        "api/notifications/",
        include("notifications.urls"),
    ),
    
]