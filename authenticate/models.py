from django.db import models
import uuid


class UserToken(models.Model):
    user_id = models.UUIDField(default=uuid.uuid4)
    token = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_admin        = models.BooleanField(default=False)
    expired_at = models.DateTimeField()


class Reset(models.Model):
    email = models.CharField(max_length=255)
    token = models.CharField(max_length=255,unique=True)