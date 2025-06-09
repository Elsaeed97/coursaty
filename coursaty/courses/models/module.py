#!/usr/bin/env python3
from django.db import models
from django.utils.translation import gettext_lazy as _


class Module(models.Model):
    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.CASCADE,
        related_name="modules",
    )
    title = models.CharField(_("Title"), max_length=255)
    description = models.TextField(_("Description"), blank=True)
    order = models.PositiveIntegerField(_("Order"), default=0)

    class Meta:
        verbose_name = _("Module")
        verbose_name_plural = _("Modules")
        ordering = ["order"]

    def __str__(self):
        return f"{self.course.title} - {self.title}"
