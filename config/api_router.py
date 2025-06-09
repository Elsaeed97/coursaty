from django.urls import include
from django.urls import path

app_name = "api"

urlpatterns = [
    path("auth/", include("coursaty.users.urls", namespace="auth")),
    path("", include("coursaty.courses.urls", namespace="courses")),
]
