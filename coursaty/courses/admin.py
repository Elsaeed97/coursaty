from django.contrib import admin

from .models import Certificate
from .models import Course
from .models import CourseCategory
from .models import Enrollment
from .models import Lesson
from .models import LessonProgress
from .models import Module


@admin.register(CourseCategory)
class CourseCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "instructor",
        "category",
        "is_free",
        "is_published",
        "created_at",
    )
    list_filter = ("is_published", "is_free", "category", "instructor")
    search_fields = ("title", "description", "instructor__email")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "order")
    list_filter = ("course",)
    search_fields = ("title", "course__title")
    ordering = ("course", "order")


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "module", "content_type", "is_published", "order")
    list_filter = ("content_type", "is_published", "module__course")
    search_fields = ("title", "module__title")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("module", "order")


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "course", "enrolled_at")
    list_filter = ("course", "enrolled_at")
    search_fields = ("student__email", "course__title")
    readonly_fields = ("enrolled_at",)


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ("student", "lesson", "completed_at")
    list_filter = ("lesson__module__course", "completed_at")
    search_fields = ("student__email", "lesson__title")
    readonly_fields = ("completed_at",)


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ("student", "course", "certificate_id", "issued_at")
    list_filter = ("course", "issued_at")
    search_fields = ("student__email", "course__title", "certificate_id")
    readonly_fields = ("certificate_id", "issued_at")
