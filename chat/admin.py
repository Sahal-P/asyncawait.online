from django.contrib import admin
from .models import Chat, Message, Notification, UserProfile, MediaMessage, Contacts

admin.site.register(Chat)
admin.site.register(Message)
admin.site.register(Notification)
admin.site.register(UserProfile)
admin.site.register(Contacts)
admin.site.register(MediaMessage)
