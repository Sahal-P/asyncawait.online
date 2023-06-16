
from django.urls import path
from django.urls import re_path
from .views import ChatAPIView

urlpatterns = [
    path('', ChatAPIView.as_view() ),
    
]