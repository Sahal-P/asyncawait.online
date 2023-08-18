from django.urls import path
from django.urls import re_path
from .views import UsersAPIView

urlpatterns = [
    path("users", UsersAPIView.as_view()),
]
