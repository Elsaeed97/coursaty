#!/usr/bin/env python3
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class LessonProgress(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    lesson = models.ForeignKey("courses.Lesson", on_delete=models.CASCADE)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "lesson")
        verbose_name = _("Lesson Progress")
        verbose_name_plural = _("Lesson Progresses")

    def __str__(self):
        return f"{self.student} completed {self.lesson.title} on {self.completed_at}"

    @classmethod
    def mark_lesson_complete(cls, student, lesson):
        """Mark a lesson as completed for a student"""
        progress, created = cls.objects.get_or_create(student=student, lesson=lesson)
        return progress, created
