
from django.urls import path
from django.urls import re_path
from .views import RegisterAPIView, UserAPIView,FriendsAPIView

urlpatterns = [
    path('', UserAPIView.as_view() ),
    path('friends', FriendsAPIView.as_view() ),
    path('register', RegisterAPIView.as_view() ),
]