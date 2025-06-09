# coursaty/courses/views/module.py
from django.core.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiParameter
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets

from coursaty.courses.api.permissions import IsCourseOwnerOrEnrolledStudent
from coursaty.courses.api.serializers.module import ModuleSerializer
from coursaty.courses.models import Module


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="course",
            type=int,
            location=OpenApiParameter.QUERY,
            description="Filter modules by course ID",
        ),
    ],
)
class ModuleViewSet(viewsets.ModelViewSet):
    queryset = Module.objects.select_related("course", "course__instructor")
    serializer_class = ModuleSerializer
    permission_classes = [IsCourseOwnerOrEnrolledStudent]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["course"]

    def get_queryset(self):
        user = self.request.user
        base = Module.objects.select_related("course", "course__instructor")

        if not user.is_authenticated:
            return base.none()

        if user.is_instructor:
            return base.filter(course__instructor=user)

        if user.is_student:
            return base.filter(course__enrollments__student=user).distinct()

        return base.none()

    def perform_create(self, serializer):
        course = serializer.validated_data["course"]
        if course.instructor != self.request.user:
            msg = "You can only add modules to your own courses."
            raise PermissionDenied(msg)
        serializer.save()
