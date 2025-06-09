import uuid

import pytest
from rest_framework import status


def test_certificate_grant(api_client, student, course, lesson):
    # Setup
    course.enrollments.create(student=student)
    lesson.mark_complete(student)

    api_client.force_authenticate(user=student)
    response = api_client.get(f"/api/courses/{course.id}/certificate/")
    assert response.status_code == status.HTTP_200_OK
    assert "certificate_id" in response.data


@pytest.mark.django_db
def test_verify_valid_certificate(api_client, certificate):
    url = f"/api/certificates/{certificate.certificate_id}/verify/"
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["certificate_id"] == str(certificate.certificate_id)


@pytest.mark.django_db
def test_verify_invalid_certificate(api_client):
    invalid_id = uuid.uuid4()
    url = f"/api/certificates/{invalid_id}/verify/"
    response = api_client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data["detail"] == "Invalid certificate ID."
