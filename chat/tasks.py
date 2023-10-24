from celery import shared_task
from chat.models import  Message
from account.models import User
from datetime import datetime
from chat.types import MESSAGE_TYPE
from account.serializers import UUIDField


@shared_task
def shared_task1():
    for i in range(10):
        print('celery',i)
    return

@shared_task
def save_message(chat_id, message, message_id):
    try:
        dt_timestamp = datetime.strptime(message["timestampe"], "%Y-%m-%d %H:%M:%S.%f")
        sender = User.objects.get(id=message["sender"])
        obj = Message.objects.create(
            id=message_id,
            chat_id=chat_id,
            sender=sender,  
            content=message["content"],
            timestampe=dt_timestamp,
            status="SENT",
        )
    except Exception as e:
        pass

@shared_task
def save_message_status(msg_type, id ):
    try:
        if "MESSAGE_READED" == MESSAGE_TYPE[msg_type]:
            status = "SEEN"
        if "MESSAGE_DELIVERD" == MESSAGE_TYPE[msg_type]:
            status = "DELIVERED"
        msg = Message.objects.get(id=id)
        msg.status=status
        msg.save()
    except Exception as e:
        pass