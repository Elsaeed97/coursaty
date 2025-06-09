from django.db import models
from django.utils.translation import gettext_lazy as _

from .progress import LessonProgress


class LessonType(models.TextChoices):
    VIDEO = "video", _("Video")
    PDF = "pdf", _("PDF")
    TEXT = "text", _("Text")


class Lesson(models.Model):
    module = models.ForeignKey(
        "courses.Module",
        on_delete=models.CASCADE,
        related_name="lessons",
    )
    title = models.CharField(_("Title"), max_length=255)
    content_type = models.CharField(
        _("Content Type"),
        choices=LessonType,
        max_length=10,
    )
    video_url = models.URLField(_("Video URL"), blank=True, null=True)  # noqa: DJ001
    pdf = models.FileField(
        _("PDF File"),
        upload_to="lessons/pdfs/",
        blank=True,
        null=True,
    )
    text = models.TextField(_("Text Content"), blank=True, null=True)  # noqa: DJ001
    duration = models.DurationField(
        _("Duration"),
        blank=True,
        null=True,
        help_text=_("Estimated time to complete this lesson"),
    )
    order = models.PositiveIntegerField(_("Order"), default=0)
    is_published = models.BooleanField(_("Published"), default=False)
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)

    class Meta:
        verbose_name = _("Lesson")
        verbose_name_plural = _("Lessons")
        ordering = ["order"]

    def __str__(self):
        return self.title

    def publish(self):
        self.is_published = True
        self.save(update_fields=["is_published"])

    def is_accessible_by(self, user):
        return self.is_published or self.module.course.instructor == user

    def mark_complete(self, student):
        LessonProgress.objects.get_or_create(student=student, lesson=self)

    def is_completed_by(self, student):
        return LessonProgress.objects.filter(student=student, lesson=self).exists()
