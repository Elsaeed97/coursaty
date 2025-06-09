from rest_framework import status


def test_lesson_create(api_client, instructor, module):
    api_client.force_authenticate(user=instructor)
    response = api_client.post(
        "/api/lessons/",
        {
            "title": "Lesson 1",
            "content_type": "text",
            "text": "content",
            "module": module.id,
        },
    )
    assert response.status_code == status.HTTP_201_CREATED


def test_lesson_visibility_for_enrolled_student(api_client, student, course, lesson):
    course.enrollments.create(student=student)
    api_client.force_authenticate(user=student)
    response = api_client.get(f"/api/lessons/?module={lesson.module.id}")
    assert response.status_code == status.HTTP_200_OK
