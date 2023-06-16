from django.contrib import admin

# Register your models here.
from .models import Chat, Message, Notification, UserProfile, MediaMessage

admin.site.register(Chat)
admin.site.register(Message)
admin.site.register(Notification)
admin.site.register(UserProfile)
admin.site.register(MediaMessage)