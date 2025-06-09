#!/usr/bin/env python3
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Enrollment(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.CASCADE,
        related_name="enrollments",
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "course")
        verbose_name = _("Enrollment")
        verbose_name_plural = _("Enrollments")

    def __str__(self):
        return f"{self.student} enrolled in {self.course.title}"

    @classmethod
    def enroll(cls, student, course):
        return cls.objects.get_or_create(student=student, course=course)
