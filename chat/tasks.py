from celery import shared_task
from .models import Chat, MediaMessage, Message, UserProfile
from account.models import User
from datetime import datetime
from .consumer import MESSAGE_TYPE

@shared_task
def shared_task():
    for i in range(10):
        print('celery',i)
    return

@shared_task
def save_message(chat, message, message_id):
    dt_timestamp = datetime.strptime(message["timestampe"], "%Y-%m-%d %H:%M:%S.%f")
    sender = User.objects.get(id=message["sender"])
    obj = Message.objects.create(
        id=message_id,
        chat=chat,
        sender=sender,  
        content=message["content"],
        timestampe=dt_timestamp,
        status="SENT",
    )

@shared_task
def save_message_status(msg_type, id ):
    if "MESSAGE_READED" == MESSAGE_TYPE[msg_type]:
        status = "SEEN"
    if "MESSAGE_DELIVERD" == MESSAGE_TYPE[msg_type]:
        status = "DELIVERED"
    msg = Message.objects.get(id=id)
    msg.status=status
    msg.save()