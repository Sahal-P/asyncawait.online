from django.db import models
from account.models import User
from datetime import datetime
import uuid


class Chat(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    participants = models.ManyToManyField(User, related_name='chat')
    is_group_chat = models.BooleanField(default=False)
    
class Message(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SENT', 'Sent'),
        ('DELIVERED', 'Delivered'),
        ('SEEN', 'Seen'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_message')
    content = models.TextField()
    timestampe = models.DateTimeField(default=datetime.now)
    has_replay = models.BooleanField(default=False)
    replay_to_msg = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    is_read = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    
class UserProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    STATUS_CHOICES = [
        ('OFFLINE', 'Offline'),
        ('ONLINE', 'Online'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_picture = models.ImageField(upload_to='profile_pictures', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OFFLINE')
    last_seen = models.DateTimeField(null=True, blank=True)

class Contacts(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_contacts')
    contact = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contact_contacts')
    is_favorite = models.BooleanField(default=False)
    is_accepted = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.contact.username}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if Contacts.objects.filter(user=self.contact,contact=self.contact).exists():
            pass
        else:
            reverse_contact, _ = Contacts.objects.get_or_create(
                user=self.contact,
                contact=self.user,
                is_favorite=self.is_favorite,
                is_accepted=self.is_accepted,
                is_blocked=self.is_blocked
            )
    
class MediaMessage(Message):
    media_file = models.FileField(upload_to='media_messages')

class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)