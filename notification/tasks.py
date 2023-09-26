from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from chat.models import Notification
import time

@shared_task
def send_websocket_notification(reciever,message,sender):
    room_group_name = reciever
    time.sleep(10)
    # Send the WebSocket notification to the user's group
    async_to_sync(get_channel_layer().group_send)(
        room_group_name,
        {
            "type": "send_notification",
            "message": message,
            "sender": sender,
        }
    )
    Notification.objects.create(
        user_id=reciever,
        sender=sender,
        message=message,
    )