from django.urls import path
from django.urls import re_path
from .views import RegisterAPIView, UserAPIView, UsersAPIView

urlpatterns = [
    path("", UserAPIView.as_view()),
    path("users", UsersAPIView.as_view()),
    path("register", RegisterAPIView.as_view()),
]
