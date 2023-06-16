from django.db import models

# Create your models here.
from account.models import User

class Chat(models.Model):
    participants = models.ManyToManyField(User, related_name='chat')
    is_group_chat = models.BooleanField(default=False)
    
class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_message')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_picture = models.ImageField(upload_to='profile_pictures', blank=True, null=True)
    status = models.CharField(max_length=255)
    last_seen = models.DateTimeField(null=True, blank=True)
    
class MediaMessage(Message):
    media_file = models.FileField(upload_to='media_messages')

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)