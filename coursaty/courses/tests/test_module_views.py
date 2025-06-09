# tests/courses/test_module_views.py

import pytest
from rest_framework import status

from coursaty.courses.models import Module
from coursaty.users.models import User


@pytest.mark.django_db
def test_instructor_can_create_module(api_client, instructor, course):
    api_client.force_authenticate(user=instructor)
    payload = {
        "title": "Module 1",
        "course": course.id,
        "description": "Basics",
        "order": 1,
    }
    response = api_client.post("/api/modules/", payload)
    assert response.status_code == status.HTTP_201_CREATED
    assert Module.objects.filter(title="Module 1", course=course).exists()


@pytest.mark.django_db
def test_other_instructor_cannot_create_module(api_client, instructor, course):
    # Different instructor
    other = User.objects.create_user(
        email="other@inst.com",
        password="123",  # noqa: S106
        role="instructor",
    )
    api_client.force_authenticate(user=other)

    response = api_client.post(
        "/api/modules/",
        {"title": "Hack", "course": course.id, "description": "Should fail"},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_student_can_list_enrolled_course_modules(api_client, student, course, module):
    course.enrollments.create(student=student)
    api_client.force_authenticate(user=student)

    response = api_client.get(f"/api/modules/?course={course.id}")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) >= 1


@pytest.mark.django_db
def test_student_cannot_see_unenrolled_course_modules(api_client, student, course):
    api_client.force_authenticate(user=student)
    response = api_client.get(f"/api/modules/?course={course.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["results"] == []


@pytest.mark.django_db
def test_unauthenticated_user_cannot_access_modules(api_client, course):
    response = api_client.get(f"/api/modules/?course={course.id}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
