from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated

from coursaty.courses.api.serializers.progress import LessonProgressSerializer
from coursaty.courses.models import LessonProgress


class LessonProgressViewSet(viewsets.ModelViewSet):
    queryset = LessonProgress.objects.select_related(
        "lesson",
        "lesson__module",
        "lesson__module__course",
    )
    serializer_class = LessonProgressSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["lesson"]

    def get_queryset(self):
        return self.queryset.filter(student=self.request.user)

    def perform_create(self, serializer):
        lesson = serializer.validated_data["lesson"]
        course = lesson.module.course

        # Ensure user is a student and enrolled
        user = self.request.user
        if not user.is_student:
            msg = "Only students can track progress."
            raise PermissionDenied(msg)

        if not course.has_student(user):
            msg = "You must be enrolled to mark progress."
            raise PermissionDenied(msg)

        if not lesson.is_accessible_by(user):
            msg = "This lesson is not yet accessible to you."
            raise PermissionDenied(msg)

        # Create or ignore if already exists
        obj, created = LessonProgress.objects.get_or_create(
            student=user,
            lesson=lesson,
        )
        if not created:
            msg = "Lesson already marked as completed."
            raise ValidationError(msg)
        serializer.instance = obj
