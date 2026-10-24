from .models import Notification


def create_application_received_notification(application):
    recruiter = application.job.recruiter

    # Skip the notification if no recruiter is assigned.
    if recruiter is None:
        return None

    return Notification.objects.create(
        recipient=recruiter.user,
        notification_type=Notification.NotificationType.APPLICATION_RECEIVED,
        title="New Application Received",
        message=(
            f"A candidate has applied for the "
            f"{application.job.title} position."
        ),
        related_job=application.job,
        related_application=application,
    )


def create_application_status_notification(application):
    candidate = application.candidate.user

    return Notification.objects.create(
        recipient=candidate,
        notification_type=Notification.NotificationType.APPLICATION_STATUS,
        title="Application Status Updated",
        message=(
            f"Your application for {application.job.title} "
            f"is now {application.get_status_display()}."
        ),
        related_job=application.job,
        related_application=application,
    )
