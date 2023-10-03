from django.db import models
from account.models import User
from datetime import datetime
import uuid
from django.core.validators import MinValueValidator, MaxValueValidator



class Chat(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    participants = models.ManyToManyField(User, related_name="chat")
    is_group_chat = models.BooleanField(default=False)


class Message(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("SENT", "Sent"),
        ("DELIVERED", "Delivered"),
        ("SEEN", "Seen"),
    ]
    id = models.UUIDField(primary_key=True, editable=False)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sent_message"
    )
    content = models.TextField()
    timestampe = models.DateTimeField()
    has_replay = models.BooleanField(default=False)
    replay_to_msg = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    is_read = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    is_deleted_for_me = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)


class UserProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    STATUS_CHOICES = [
        ("OFFLINE", "Offline"),
        ("ONLINE", "Online"),
    ]
    AVATAR_CHOICES = [
        ( "images/avatar/default_avatar_1.png","default"),
        ("images/avatar/1.png", "1"),
        ("images/avatar/2.png", "2"),
        ("images/avatar/3.png", "3"),
        ("images/avatar/4.png", "4"),
        ("images/avatar/5.png", "5"),
        ("images/avatar/6.png", "6"),
        ("images/avatar/7.png", "7"),
        ("images/avatar/8.png", "8"),
        ("images/avatar/9.png", "9"),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    profile_picture = models.ImageField(
        upload_to="images/profile_pictures", null=True, blank=True
    )
    picture_blurhash = models.CharField(max_length=200, null=True, blank=True)
    default_avatar = models.CharField(
      choices=AVATAR_CHOICES, default="images/avatar/default_avatar_1.png", null=True, blank=True
    )
    username = models.CharField(max_length=100, null=True, blank=True)
    about = models.CharField(max_length=200, null=True, blank=True)
    
    status = models.CharField(choices=STATUS_CHOICES, default="OFFLINE")
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(null=True, blank=True)


class Contacts(models.Model):
    LAST_ACTIVITY_CHOICES = [
        ("MESSAGE", "Message"),
        ("IMAGE", "Image"),
        ("AUDIO", "Audio"),
        ("CALL", "Call"),
        ("NEW", "New"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_contacts"
    )
    contact = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="contact_contacts"
    )
    last_activity_type = models.CharField(choices=LAST_ACTIVITY_CHOICES, default="New")
    last_activity = models.CharField(max_length=200, null=True, blank=True)
    last_activity_time = models.DateTimeField(null=True)
    unread_count = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)], default=0)
    is_favorite = models.BooleanField(default=False)
    is_accepted = models.BooleanField(default=False)
    is_muted = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.contact.username}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if Contacts.objects.filter(user=self.contact, contact=self.contact).exists():
            pass
        else:
            reverse_contact, _ = Contacts.objects.get_or_create(
                user=self.contact,
                contact=self.user,
                is_favorite=self.is_favorite,
                is_accepted=self.is_accepted,
                is_blocked=self.is_blocked,
            )

class MediaMessage(Message):
    MEDIA_TYPE_CHOICES = [
        ("DOCUMENT", "Document"),
        ("AUDIO", "Audio"),
        ("VIDEO", "Video"),
        ("IMAGE", "Image"),
        ("DEFAULT", "None"),
    ]
    media_file = models.FileField(upload_to="media_messages")
    media_type = models.CharField(choices=MEDIA_TYPE_CHOICES, default="DEFAULT")
    image_blurhash = models.CharField(max_length=200, null=True, blank=True)


class Notification(models.Model):
    MSG_TYPE_CHOICES = [
        ("TEXT", "Text"),
        ("AUDIO", "Audio"),
        ("VIDEO", "Video"),
        ("IMAGE", "Image"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications"
    )
    sender = models.CharField(max_length=200, null=True, blank=True)
    message = models.TextField()
    message_type = models.CharField(choices=MSG_TYPE_CHOICES, default="Text")
    timestamp = models.DateTimeField()
    is_read = models.BooleanField(default=False)
