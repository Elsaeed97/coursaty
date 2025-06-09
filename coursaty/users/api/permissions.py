from rest_framework.permissions import BasePermission


class IsStudent(BasePermission):
    """
    Custom permission to only allow students to access certain views.
    """

    def has_permission(self, request, view):
        # Check if the user is authenticated and has the 'student' role
        return request.user.is_authenticated and request.user.role == "student"


class IsInstructor(BasePermission):
    """
    Custom permission to only allow instructors to access certain views.
    """

    def has_permission(self, request, view):
        # Check if the user is authenticated and has the 'instructor' role
        return request.user.is_authenticated and request.user.role == "instructor"
