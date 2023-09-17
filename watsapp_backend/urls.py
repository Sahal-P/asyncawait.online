from django.urls import path, include
from django.urls import re_path
from . import consumer
from chat.consumer import ChatConsumer
import debug_toolbar
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("__debug__/", include(debug_toolbar.urls)),
    path("", include("account.urls")),
    path("auth/", include("authenticate.urls")),
    path("chat/", include("chat.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

websocket_urlpatterns = [
    re_path(r"ws/socket/user/(?P<room_name>[0-9a-f-]+)/$", consumer.UserConnection.as_asgi()),
    re_path(r"ws/chat/(?P<room_name>[0-9a-f-]+)/$", ChatConsumer.as_asgi()),
] 
