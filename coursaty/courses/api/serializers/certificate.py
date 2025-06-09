from rest_framework import serializers

from coursaty.courses.models import Certificate


class CertificateSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.name", read_only=True)
    course_title = serializers.CharField(source="course.title", read_only=True)

    class Meta:
        model = Certificate
        fields = [
            "certificate_id",
            "student_name",
            "course_title",
            "issued_at",
        ]
