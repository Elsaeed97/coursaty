import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from coursaty.courses.models import Certificate
from coursaty.courses.models import Course
from coursaty.courses.models import CourseCategory
from coursaty.courses.models import Enrollment
from coursaty.courses.models import Lesson
from coursaty.courses.models import Module

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def instructor(db):
    return User.objects.create_user(
        email="instructor@test.com",
        password="test123",  # noqa: S106
        role="instructor",
    )


@pytest.fixture
def student(db):
    return User.objects.create_user(
        email="student@test.com",
        password="test123",  # noqa: S106
        role="student",
    )


@pytest.fixture
def category(db):
    return CourseCategory.objects.create(name="Programming", slug="programming")


@pytest.fixture
def course(instructor, category):
    return Course.objects.create(
        title="Django Basics",
        instructor=instructor,
        is_published=True,
        category=category,
    )


@pytest.fixture
def enrolled_course(course, student):
    Enrollment.objects.create(course=course, student=student)
    return course


@pytest.fixture
def module(course):
    return Module.objects.create(course=course, title="Module 1")


@pytest.fixture
def lesson(module):
    return Lesson.objects.create(
        module=module,
        title="Lesson 1",
        content_type="text",
        text="Some content",
        is_published=True,
    )


@pytest.fixture
def certificate(student, course):
    return Certificate.objects.create(student=student, course=course)
