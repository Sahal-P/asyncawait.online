from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User
from chat.models import UserProfile


@receiver(post_save, sender=User)
def profile_save_handler(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    print("user saved")
    print("instance", instance)
    print("created", created)
