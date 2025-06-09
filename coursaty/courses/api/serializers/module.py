# coursaty/courses/serializers/module.py

from rest_framework import serializers

from coursaty.courses.models import Module


class ModuleSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source="course.title", read_only=True)

    class Meta:
        model = Module
        fields = [
            "id",
            "course",
            "course_title",
            "title",
            "description",
            "order",
        ]
