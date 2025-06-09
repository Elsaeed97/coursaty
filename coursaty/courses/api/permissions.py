from rest_framework.permissions import BasePermission


class IsInstructorOrReadOnly(BasePermission):
    """
    Permission that allows instructors to create/edit,
    and students to only read.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # Instructors have full access
        if request.user.is_instructor:
            return True

        # Students have read-only access
        if request.user.is_student:
            return request.method in ["GET", "HEAD", "OPTIONS"]

        return False


class IsCourseOwnerOrEnrolledStudent(BasePermission):
    """
    Permission that allows:
    - Course instructors to manage their own courses
    - Enrolled students to read course content
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Get the course object
        course = self._get_course(obj)
        if not course:
            return False

        # Instructors can manage their own courses
        if request.user.is_instructor:
            return course.instructor == request.user

        # Students can only read enrolled courses
        if request.user.is_student:
            if request.method in ["GET", "HEAD", "OPTIONS"]:
                return course.has_student(request.user)

        return False

    def _get_course(self, obj):
        """Helper method to get course from different object types"""
        if hasattr(obj, "course"):  # Module, Lesson, Enrollment
            return obj.course
        elif hasattr(obj, "enrollments"):  # Course # noqa: RET505
            return obj
        return None


class IsEnrolledStudent(BasePermission):
    """
    Permission for enrolled students only.
    Used for progress tracking and course content access.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_student

    def has_object_permission(self, request, view, obj):
        course = self._get_course(obj)
        if not course:
            return False

        return course.has_student(request.user)

    def _get_course(self, obj):
        """Helper method to get course from different object types"""
        if hasattr(obj, "course"):
            return obj.course
        elif hasattr(obj, "lesson") and hasattr(obj.lesson, "module"):  # noqa: RET505
            return obj.lesson.module.course
        elif hasattr(obj, "enrollments"):
            return obj
        return None


class IsInstructorOwner(BasePermission):
    """
    Permission for instructors to manage only their own content.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_instructor

    def has_object_permission(self, request, view, obj):
        course = self._get_course(obj)
        if not course:
            return False

        return course.instructor == request.user

    def _get_course(self, obj):
        """Helper method to get course from different object types"""
        if hasattr(obj, "instructor"):  # Course
            return obj
        elif hasattr(obj, "course"):  # Module, Lesson # noqa: RET505
            return obj.course
        return None
