from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from coursaty.courses.models import Course
from coursaty.courses.models import CourseCategory


class CourseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseCategory
        fields = ["id", "name", "slug"]


class CourseSerializer(serializers.ModelSerializer):
    instructor = serializers.StringRelatedField(read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)
    modules_count = serializers.SerializerMethodField()
    students_count = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "description",
            "instructor",
            "category",
            "category_name",
            "cover_image",
            "price",
            "is_free",
            "estimated_duration",
            "is_published",
            "created_at",
            "updated_at",
            "modules_count",
            "students_count",
            "progress",
        ]
        read_only_fields = ["instructor", "created_at", "updated_at"]

    def get_modules_count(self, obj):
        return obj.modules.count()

    def get_students_count(self, obj):
        return obj.enrollments.count()

    def validate_title(self, value):
        if len(value.strip()) < 3:  # noqa: PLR2004
            msg = "Course title must be at least 3 characters long."
            raise ValidationError(msg)
        return value.strip()

    def validate_price(self, value):
        if value < 0:
            msg = "Price cannot be negative."
            raise ValidationError(msg)
        return value

    def validate_estimated_duration(self, value):
        if value is not None and value <= 0:
            msg = "Estimated duration must be greater than 0."
            raise ValidationError(msg)
        return value

    def validate(self, attrs):
        # If course is not free, price must be greater than 0
        if not attrs.get("is_free", True) and attrs.get("price", 0) <= 0:
            raise ValidationError(
                {"price": "Price must be greater than 0 for paid courses."},
            )

        # If price is 0, course should be free
        if attrs.get("price", 0) == 0:
            attrs["is_free"] = True

        return attrs

    def get_progress(self, obj):
        user = self.context["request"].user
        if not user.is_authenticated or not user.is_student:
            return None
        return obj.get_progress_summary(user)

    def create(self, validated_data):
        # Set the instructor to the current user
        validated_data["instructor"] = self.context["request"].user
        return super().create(validated_data)


class CourseListSerializer(serializers.ModelSerializer):
    """Simplified serializer for course listing"""

    instructor_name = serializers.CharField(source="instructor.name", read_only=True)
    instructor_email = serializers.CharField(source="instructor.email", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "description",
            "instructor_name",
            "instructor_email",
            "category_name",
            "cover_image",
            "price",
            "is_free",
            "estimated_duration",
            "is_published",
            "created_at",
        ]
