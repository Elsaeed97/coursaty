#!/usr/bin/env python3
from datetime import timedelta

import pytest

from coursaty.courses.models import Certificate
from coursaty.courses.models import Course
from coursaty.courses.models import CourseCategory
from coursaty.courses.models import Enrollment
from coursaty.courses.models import Lesson
from coursaty.courses.models import LessonProgress
from coursaty.courses.models import Module
from coursaty.users.models import User
from coursaty.users.models import UserRole


@pytest.fixture
def instructor(db):
    return User.objects.create_user(
        email="instructor@example.com",
        password="testpass123",  # noqa: S106
        role=UserRole.INSTRUCTOR,
    )


@pytest.fixture
def student(db):
    return User.objects.create_user(
        email="student@example.com",
        password="testpass123",  # noqa: S106
        role=UserRole.STUDENT,
    )


@pytest.fixture
def category():
    return CourseCategory.objects.create(name="Programming", slug="programming")


@pytest.fixture
def course(instructor, category):
    return Course.objects.create(
        title="Python 101",
        description="Intro to Python",
        instructor=instructor,
        category=category,
    )


@pytest.fixture
def module(course):
    return Module.objects.create(
        course=course,
        title="Basics",
        description="Basic Python concepts and syntax",
        order=1,
    )


@pytest.fixture
def lesson(module):
    return Lesson.objects.create(
        module=module,
        title="Lesson 1",
        content_type="text",
        text="Hello world",
        duration=timedelta(minutes=15),
        order=1,
        is_published=False,
    )


@pytest.fixture
def video_lesson(module):
    return Lesson.objects.create(
        module=module,
        title="Video Lesson",
        content_type="video",
        video_url="https://example.com/video.mp4",
        duration=timedelta(minutes=30),
        order=2,
        is_published=True,
    )


# ------------------------
# COURSE MODEL TESTS
# ------------------------


def test_course_str(course):
    assert str(course) == "Python 101"


def test_course_publish(course):
    assert not course.is_published
    course.publish()
    course.refresh_from_db()
    assert course.is_published


def test_course_accessibility(course, instructor, student):
    assert not course.is_accessible_by(student)
    assert course.is_accessible_by(instructor)
    course.publish()
    assert course.is_accessible_by(student)


def test_course_has_student(course, student):
    assert not course.has_student(student)
    Enrollment.enroll(student, course)
    assert course.has_student(student)


def test_course_total_lessons(course, lesson, video_lesson):
    total_lessons = 2
    assert course.total_lessons() == total_lessons


def test_course_completed_lessons_count(course, student, lesson, video_lesson):
    total_lessons = 2
    assert course.completed_lessons_count(student) == 0

    lesson.mark_complete(student)
    assert course.completed_lessons_count(student) == 1

    video_lesson.mark_complete(student)
    assert course.completed_lessons_count(student) == total_lessons


def test_course_completion(course, student, lesson, video_lesson):
    assert not course.is_completed_by(student)

    lesson.mark_complete(student)
    assert not course.is_completed_by(student)

    video_lesson.mark_complete(student)
    assert course.is_completed_by(student)


# ------------------------
# MODULE MODEL TESTS
# ------------------------


def test_module_str(module):
    assert str(module) == "Python 101 - Basics"


def test_module_description(module):
    assert module.description == "Basic Python concepts and syntax"


# ------------------------
# LESSON MODEL TESTS
# ------------------------


def test_lesson_str(lesson):
    assert str(lesson) == "Lesson 1"


def test_lesson_publish(lesson):
    assert not lesson.is_published
    lesson.publish()
    lesson.refresh_from_db()
    assert lesson.is_published


def test_lesson_accessibility(lesson, instructor, student):
    assert not lesson.is_accessible_by(student)
    assert lesson.is_accessible_by(instructor)
    lesson.publish()
    assert lesson.is_accessible_by(student)


def test_lesson_duration(lesson):
    assert lesson.duration == timedelta(minutes=15)


def test_lesson_content_types(lesson, video_lesson):
    assert lesson.content_type == "text"
    assert lesson.text == "Hello world"

    assert video_lesson.content_type == "video"
    assert video_lesson.video_url == "https://example.com/video.mp4"


def test_lesson_is_completed_by(lesson, student):
    assert not lesson.is_completed_by(student)
    lesson.mark_complete(student)
    assert lesson.is_completed_by(student)


# ------------------------
# ENROLLMENT & PROGRESS
# ------------------------


def test_enrollment(student, course):
    enrollment, created = Enrollment.enroll(student, course)
    assert created
    assert enrollment.student == student
    assert enrollment.course == course

    # Test that duplicate enrollment doesn't create new record
    enrollment2, created2 = Enrollment.enroll(student, course)
    assert not created2
    assert enrollment == enrollment2


def test_enrollment_str(student, course):
    enrollment, _ = Enrollment.enroll(student, course)
    expected = f"{student} enrolled in {course.title}"
    assert str(enrollment) == expected


def test_mark_lesson_complete(student, lesson):
    lesson.mark_complete(student)
    assert LessonProgress.objects.filter(student=student, lesson=lesson).exists()


def test_lesson_progress_mark_complete(student, lesson):
    progress, created = LessonProgress.mark_lesson_complete(student, lesson)
    assert created
    assert progress.student == student
    assert progress.lesson == lesson

    # Test duplicate completion doesn't create new record
    progress2, created2 = LessonProgress.mark_lesson_complete(student, lesson)
    assert not created2
    assert progress == progress2


def test_lesson_progress_str(student, lesson):
    progress, _ = LessonProgress.mark_lesson_complete(student, lesson)
    expected = f"{student} completed {lesson.title} on {progress.completed_at}"
    assert str(progress) == expected


# ------------------------
# CERTIFICATE
# ------------------------


def test_certificate_issue(student, course):
    cert, created = Certificate.issue(student, course)
    assert created
    assert cert.student == student
    assert cert.course == course
    assert cert.certificate_id

    # Test duplicate certificate doesn't create new record
    cert2, created2 = Certificate.issue(student, course)
    assert not created2
    assert cert == cert2


def test_certificate_str(student, course):
    cert, _ = Certificate.issue(student, course)
    expected = f"Certificate for {student.name or student.email} in {course.title}"
    assert str(cert) == expected


def test_certificate_verify(student, course):
    cert, _ = Certificate.issue(student, course)

    # Test valid certificate verification
    verified_cert = Certificate.verify_certificate(cert.certificate_id)
    assert verified_cert == cert

    # Test invalid certificate ID
    import uuid

    invalid_cert = Certificate.verify_certificate(uuid.uuid4())
    assert invalid_cert is None


# ------------------------
# INTEGRATION TESTS
# ------------------------


def test_full_course_workflow(course, student, instructor, lesson, video_lesson):
    """Test complete workflow from enrollment to certificate"""

    # Instructor publishes course and lessons
    course.publish()
    lesson.publish()
    video_lesson.publish()

    # Student enrolls
    enrollment, created = Enrollment.enroll(student, course)
    assert created
    assert course.has_student(student)

    # Student progresses through lessons
    assert course.completed_lessons_count(student) == 0

    lesson.mark_complete(student)
    assert course.completed_lessons_count(student) == 1
    assert not course.is_completed_by(student)

    video_lesson.mark_complete(student)
    total_lessons = 2
    assert course.completed_lessons_count(student) == total_lessons
    assert course.is_completed_by(student)

    # Certificate can be issued
    cert, created = Certificate.issue(student, course)
    assert created
