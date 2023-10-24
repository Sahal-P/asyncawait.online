from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification, UserProfile
from django.core.cache import cache

@receiver(post_save, sender=Notification)
def send_notification_on_save(sender, instance, **kwargs):
    pass
    # Get the user's room_group_name from the Notification's user
    # room_group_name = "f2f0fd53-20c0-49c6-8ed6-fcc6005028ad"

    # # Send the WebSocket notification to the user's group
    # async_to_sync(get_channel_layer().group_send)(
    #     room_group_name,
    #     {
    #         "type": "send_notification",
    #         "message": instance.message,
    #     }
    # )

@receiver(post_save, sender=UserProfile)
def clear_usersapiview_cache(sender, instance, **kwargs):
    # Trigger the custom management command to clear cache
    cache_key_prefix = "UsersAPIVIEW"
    cache.delete_pattern(f"{cache_key_prefix}*")