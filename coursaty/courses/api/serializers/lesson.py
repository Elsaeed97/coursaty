# coursaty/courses/serializers/lesson.py

from rest_framework import serializers

from coursaty.courses.models import Lesson
from coursaty.courses.models import LessonType


class LessonSerializer(serializers.ModelSerializer):
    module_title = serializers.CharField(source="module.title", read_only=True)
    course_title = serializers.CharField(source="module.course.title", read_only=True)

    class Meta:
        model = Lesson
        fields = [
            "id",
            "module",
            "module_title",
            "course_title",
            "title",
            "content_type",
            "video_url",
            "pdf",
            "text",
            "duration",
            "order",
            "is_published",
            "created_at",
            "updated_at",
        ]

    def validate(self, data):
        content_type = data.get("content_type")
        if content_type == LessonType.VIDEO and not data.get("video_url"):
            raise serializers.ValidationError(
                {"video_url": "Video URL is required for video lessons."},
            )
        if content_type == LessonType.PDF and not data.get("pdf"):
            raise serializers.ValidationError(
                {"pdf": "PDF file is required for PDF lessons."},
            )
        if content_type == LessonType.TEXT and not data.get("text"):
            raise serializers.ValidationError(
                {"text": "Text content is required for text lessons."},
            )
        return data
