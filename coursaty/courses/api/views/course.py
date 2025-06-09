from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from coursaty.courses.api.permissions import IsCourseOwnerOrEnrolledStudent
from coursaty.courses.api.permissions import IsEnrolledStudent
from coursaty.courses.api.permissions import IsInstructorOrReadOnly
from coursaty.courses.api.serializers import CourseCategorySerializer
from coursaty.courses.api.serializers import CourseListSerializer
from coursaty.courses.api.serializers import CourseSerializer
from coursaty.courses.api.serializers.certificate import CertificateSerializer
from coursaty.courses.models import Certificate
from coursaty.courses.models import Course
from coursaty.courses.models import CourseCategory
from coursaty.courses.models import Enrollment


class CourseCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for course categories (read-only for all users)
    """

    queryset = CourseCategory.objects.all()
    serializer_class = CourseCategorySerializer
    permission_classes = [IsAuthenticated]


class CourseViewSet(viewsets.ModelViewSet):
    """
    ViewSet for course management
    """

    queryset = Course.objects.select_related("instructor", "category").prefetch_related(
        "enrollments",
    )
    permission_classes = [IsInstructorOrReadOnly, IsCourseOwnerOrEnrolledStudent]

    def get_serializer_class(self):
        if self.action == "list":
            return CourseListSerializer
        return CourseSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = self.queryset

        if user.is_instructor:
            return queryset.filter(instructor=user)
        elif user.is_student:  # noqa: RET505
            return queryset.filter(is_published=True)

        return queryset.none()

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        """Action to publish a course"""
        course = self.get_object()

        # Check if course has at least one module with one lesson
        if not course.modules.exists():
            return Response(
                {"error": "Course must have at least one module before publishing."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        has_lessons = any(module.lessons.exists() for module in course.modules.all())
        if not has_lessons:
            return Response(
                {"error": "Course must have at least one lesson before publishing."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        course.publish()
        serializer = self.get_serializer(course)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def unpublish(self, request, pk=None):
        """Action to unpublish a course"""
        course = self.get_object()
        course.is_published = False
        course.save(update_fields=["is_published"])

        serializer = self.get_serializer(course)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def my_courses(self, request):
        """Get courses created by the current instructor"""
        if not request.user.is_instructor:
            return Response(
                {"error": "Only instructors can access this endpoint."},
                status=status.HTTP_403_FORBIDDEN,
            )

        courses = self.queryset.filter(instructor=request.user)
        serializer = self.get_serializer(courses, many=True)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=["post"],
        url_path="enroll",
        permission_classes=[IsAuthenticated],
    )
    def enroll(self, request, pk=None):
        course = self.get_object()
        user = request.user

        if not user.is_student:
            msg = "Only students can enroll in courses."
            raise PermissionDenied(msg)

        if Enrollment.objects.filter(student=user, course=course).exists():
            msg = "You are already enrolled in this course."
            raise ValidationError(msg)

        Enrollment.objects.create(student=user, course=course)
        return Response(
            {"detail": "Successfully enrolled."},
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["get"], permission_classes=[IsEnrolledStudent])
    def progress(self, request, pk=None):
        course = self.get_object()
        return Response(course.get_progress_summary(request.user))

    @action(detail=True, methods=["get"], permission_classes=[IsEnrolledStudent])
    def certificate(self, request, pk=None):
        course = self.get_object()

        if not course.is_completed_by(request.user):
            msg = "You must complete all lessons before receiving a certificate."
            raise ValidationError(
                msg,
            )

        cert, _ = Certificate.issue(request.user, course)
        return Response(CertificateSerializer(cert).data)
