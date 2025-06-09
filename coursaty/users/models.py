from typing import ClassVar

from django.contrib.auth.models import AbstractUser
from django.db.models import CharField
from django.db.models import EmailField
from django.db.models import TextChoices
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from .managers import UserManager


class UserRole(TextChoices):
    STUDENT = "student", "Student"
    INSTRUCTOR = "instructor", "Instructor"


class User(AbstractUser):
    """
    Custom user model for the LMS system with role-based access (student, instructor).
    """

    # First and last name do not cover name patterns around the globe
    name = CharField(_("Name of User"), blank=True, max_length=255)
    first_name = None  # type: ignore[assignment]
    last_name = None  # type: ignore[assignment]
    email = EmailField(_("email address"), unique=True)
    username = None  # type: ignore[assignment]
    role = CharField(
        max_length=15,
        choices=UserRole,
        default=UserRole.STUDENT,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects: ClassVar[UserManager] = UserManager()

    @property
    def is_student(self) -> bool:
        return self.role == UserRole.STUDENT

    @property
    def is_instructor(self) -> bool:
        return self.role == UserRole.INSTRUCTOR

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"pk": self.id})
