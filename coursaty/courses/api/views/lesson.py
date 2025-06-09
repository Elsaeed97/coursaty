# coursaty/courses/views/lesson.py

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied

from coursaty.courses.api.permissions import IsCourseOwnerOrEnrolledStudent
from coursaty.courses.api.serializers.lesson import LessonSerializer
from coursaty.courses.models import Lesson


class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.select_related(
        "module",
        "module__course",
        "module__course__instructor",
    )
    serializer_class = LessonSerializer
    permission_classes = [IsCourseOwnerOrEnrolledStudent]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["module"]

    def perform_create(self, serializer):
        module = serializer.validated_data["module"]
        course = module.course
        if course.instructor != self.request.user:
            msg = "You can only add lessons to your own course modules."
            raise PermissionDenied(msg)
        serializer.save()
