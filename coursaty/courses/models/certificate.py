import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Certificate(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey("courses.Course", on_delete=models.CASCADE)
    issued_at = models.DateTimeField(auto_now_add=True)
    certificate_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    class Meta:
        unique_together = ("student", "course")
        verbose_name = _("Certificate")
        verbose_name_plural = _("Certificates")

    def __str__(self):
        return (
            f"Certificate for {self.student.name or self.student.email} "
            f"in {self.course.title}"
        )

    @classmethod
    def issue(cls, student, course):
        """Issue a certificate for a student completing a course"""
        return cls.objects.get_or_create(student=student, course=course)

    @classmethod
    def verify_certificate(cls, certificate_id):
        """Verify a certificate by its ID"""
        try:
            return cls.objects.get(certificate_id=certificate_id)
        except cls.DoesNotExist:
            return None
