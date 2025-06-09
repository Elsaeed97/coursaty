from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from coursaty.users.models import UserRole

from .lesson import Lesson
from .progress import LessonProgress


class CourseCategory(models.Model):
    name = models.CharField(_("Category Name"), max_length=100)
    slug = models.SlugField(_("Slug"), unique=True)

    class Meta:
        verbose_name = _("Course Category")
        verbose_name_plural = _("Course Categories")

    def __str__(self):
        return self.name


class Course(models.Model):
    title = models.CharField(_("Title"), max_length=255)
    description = models.TextField(_("Description"), blank=True)
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="courses",
        limit_choices_to={"role": UserRole.INSTRUCTOR},
        verbose_name=_("Instructor"),
    )
    category = models.ForeignKey(
        "CourseCategory",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Category"),
    )
    is_published = models.BooleanField(_("Published"), default=False)
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)
    cover_image = models.ImageField(
        _("Cover Image"),
        upload_to="courses/covers/",
        blank=True,
        null=True,
    )
    price = models.DecimalField(
        _("Price"),
        max_digits=10,
        decimal_places=2,
        default=0.00,
    )
    is_free = models.BooleanField(_("Free Course"), default=True)
    estimated_duration = models.PositiveIntegerField(
        _("Duration (hours)"),
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _("Course")
        verbose_name_plural = _("Courses")

    def __str__(self):
        return self.title

    def publish(self):
        self.is_published = True
        self.save(update_fields=["is_published"])

    def is_accessible_by(self, user):
        return self.is_published or user == self.instructor

    def has_student(self, user):
        return self.enrollments.filter(student=user).exists()

    def total_lessons(self):
        return Lesson.objects.filter(module__course=self).count()

    def completed_lessons_count(self, student):
        return LessonProgress.objects.filter(
            student=student,
            lesson__module__course=self,
        ).count()

    def is_completed_by(self, student):
        return self.completed_lessons_count(student) == self.total_lessons()

    def get_progress_summary(self, student):
        if not self.has_student(student):
            return None

        total = self.total_lessons()
        completed = self.completed_lessons_count(student)
        percent = (completed / total * 100) if total else 0

        return {
            "total_lessons": total,
            "completed_lessons": completed,
            "completion_percent": round(percent, 2),
        }
