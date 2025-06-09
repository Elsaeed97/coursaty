from rest_framework import status


def test_mark_lesson_complete(api_client, student, lesson):
    lesson.module.course.enrollments.create(student=student)
    api_client.force_authenticate(user=student)

    response = api_client.post("/api/progress/", {"lesson": lesson.id})
    assert response.status_code == status.HTTP_201_CREATED

    # Can't mark twice
    response2 = api_client.post("/api/progress/", {"lesson": lesson.id})
    assert response2.status_code == status.HTTP_400_BAD_REQUEST
