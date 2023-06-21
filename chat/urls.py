
from django.urls import path
from django.urls import re_path
from .views import ChatAPIView, MessageUnknownAPIView, GetChatIDAPIView, GetContactsAPIView,GetChatDetailsAPIView

urlpatterns = [
    path('', ChatAPIView.as_view() ),
    path('unknown', MessageUnknownAPIView.as_view() ),
    path('get_chatid', GetChatIDAPIView.as_view() ),
    path('get_contacts', GetContactsAPIView.as_view() ),
    path('get_chat_details', GetChatDetailsAPIView.as_view() ),
    
]