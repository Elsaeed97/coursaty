from rest_framework import status


def test_course_list(api_client, student, course):
    api_client.force_authenticate(user=student)
    response = api_client.get("/api/courses/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) >= 1


def test_course_create_by_instructor(api_client, instructor, category):
    api_client.force_authenticate(user=instructor)
    payload = {
        "title": "New Course",
        "description": "Test description",
        "category": category.id,
        "price": "100.00",
        "estimated_duration": 15,
    }
    response = api_client.post("/api/courses/", payload)
    assert response.status_code == status.HTTP_201_CREATED


def test_course_create_denied_for_student(api_client, student, category):
    api_client.force_authenticate(user=student)
    response = api_client.post(
        "/api/courses/",
        {
            "title": "Hack Course",
            "category_id": category.id,
        },
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
