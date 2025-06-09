# coursaty/courses/urls.py
from django.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter

from coursaty.courses.api.views import CertificateVerifyView
from coursaty.courses.api.views import CourseCategoryViewSet
from coursaty.courses.api.views import CourseViewSet
from coursaty.courses.api.views import LessonProgressViewSet
from coursaty.courses.api.views import LessonViewSet
from coursaty.courses.api.views import ModuleViewSet

app_name = "courses"

router = DefaultRouter()
router.register(r"courses", CourseViewSet, basename="courses")
router.register(r"modules", ModuleViewSet, basename="modules")
router.register(r"categories", CourseCategoryViewSet, basename="categories")
router.register(r"lessons", LessonViewSet, basename="lessons")
router.register(r"progress", LessonProgressViewSet, basename="progress")


urlpatterns = [
    path("", include(router.urls)),
    path("certificates/<uuid:certificate_id>/verify/", CertificateVerifyView.as_view()),
]
