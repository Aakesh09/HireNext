from rest_framework.permissions import BasePermission


class IsAdminRole(BasePermission):
    """
    Allows access only to Admin users.
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "ADMIN"
        )


class IsRecruiterRole(BasePermission):
    """
    Allows access only to Recruiter users.
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "RECRUITER"
        )


class IsCandidateRole(BasePermission):
    """
    Allows access only to Candidate users.
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "CANDIDATE"
        )


class IsRecruiterOrAdmin(BasePermission):
    """
    Allows access to Recruiters and Admins.
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in ["RECRUITER", "ADMIN"]
        )


class IsCandidateOrAdmin(BasePermission):
    """
    Allows access to Candidates and Admins.
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in ["CANDIDATE", "ADMIN"]
        )