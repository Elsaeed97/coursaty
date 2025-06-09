# coursaty/courses/serializers/progress.py

from rest_framework import serializers

from coursaty.courses.models import LessonProgress


class LessonProgressSerializer(serializers.ModelSerializer):
    lesson_title = serializers.CharField(source="lesson.title", read_only=True)
    course_title = serializers.CharField(
        source="lesson.module.course.title",
        read_only=True,
    )

    class Meta:
        model = LessonProgress
        fields = ["id", "lesson", "lesson_title", "course_title", "completed_at"]
        read_only_fields = ["id", "lesson_title", "course_title", "completed_at"]
