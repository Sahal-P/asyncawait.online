from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
import json
from datetime import datetime
from .models import Chat, MediaMessage, Message, UserProfile
from account.models import User
import uuid
from account.uuid_serializer import UUID, UUIDEncoder
from notification.tasks import send_websocket_notification

MESSAGE_MAX_LENGTH = 100

MESSAGE_ERROR_TYPE = {
    "MESSAGE_OUT_OF_LENGTH": "MESSAGE_OUT_OF_LENGTH",
    "UN_AUTHENTICATED": "UN_AUTHENTICATED",
    "INVALID_MESSAGE": "INVALID_MESSAGE",
}

MESSAGE_TYPE = {
    "WENT_ONLINE": "WENT_ONLINE",
    "WENT_OFFLINE": "WENT_OFFLINE",
    "IS_TYPING": "IS_TYPING",
    "NOT_TYPING": "NOT_TYPING",
    "MESSAGE_COUNTER": "MESSAGE_COUNTER",
    "OVERALL_MESSAGE_COUNTER": "OVERALL_MESSAGE_COUNTER",
    "TEXT_MESSAGE": "TEXT_MESSAGE",
    "MESSAGE_READED": "MESSAGE_READED",
    "ALL_MESSAGE_READ": "ALL_MESSAGE_READ",
    "MESSAGE_DELIVERD": "MESSAGE_DELIVERD",
    "MESSAGE_DELETE_FOR_ME": "MESSAGE_DELETE_FOR_ME",
    "MESSAGE_DELETE_FOR_EVERYONE": "MESSAGE_DELETE_FOR_EVERYONE",
    "ERROR_OCCURED": "ERROR_OCCURED",
    "MESSAGE_NOTIFICATION": "MESSAGE_NOTIFICATION",
    "USER_LEFT": "USER_LEFT",
}


class ChatConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        self.room_group_name = self.scope["url_route"]["kwargs"]["room_name"]
        print(self.room_group_name, 'chat_id')
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        self.chat = await self.get_chat_obj(self.room_group_name)
        await self.send(json.dumps({"status": "200"}))

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        content = text_data_json.get("content")
        msg_type = text_data_json.get("type")
        sender = text_data_json.get("sender")
        reciever = text_data_json.get("reciever")
        timestampe = text_data_json.get("timestampe")
        # Handle received data
        if msg_type == MESSAGE_TYPE["TEXT_MESSAGE"]:
            send_websocket_notification.delay(reciever, content, sender, timestampe)
            message_id = uuid.UUID(text_data_json.get("id"))
            # message_id = uuid.uuid4()
            id = text_data_json.get("id")
            await self.save_text_message(text_data_json, message_id)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "content": content,
                    "sender": sender,
                    "timestampe": timestampe,
                    "id": id,
                    # "temp_id":temp_id,
                },
            )
            
        elif msg_type == MESSAGE_TYPE["MESSAGE_READED"]:
            id = text_data_json.get("id")
            await self.save_message_status(msg_type, id)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "message_seen",
                    "id": id,
                    "sender": sender,
                },
            )
            
        elif msg_type == MESSAGE_TYPE["MESSAGE_DELIVERD"]:
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "message_deliverd",
                    "content": content,
                    "sender": sender,
                },
            )
        
    async def chat_message(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "message_type": MESSAGE_TYPE["TEXT_MESSAGE"],
                    "id": event["id"],
                    "content": event["content"],
                    "sender": event["sender"],
                    "timestampe": event["timestampe"],
                    # "temp_id": event["temp_id"],
                    "status": "SENT",
                }
            )
        )
        
    async def message_seen(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "message_type": MESSAGE_TYPE["MESSAGE_READED"],
                    "sender": event["sender"],
                    "id":event["id"]
                }
            )
        )
    
    async def message_deliverd(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "message_type": MESSAGE_TYPE["MESSAGE_DELIVERD"],
                    "content": event['content'],
                    "sender": event["sender"]
                }
            )
        )
    async def send_notification(self, event):        
        await self.send(
            text_data=json.dumps(
                {
                    "message_type": MESSAGE_TYPE["MESSAGE_NOTIFICATION"],
                    "content": event['message'],
                    "sender": event['sender'],
                }
            )
        )

    async def disconnect(self, code):
        await self.channel_layer.group_send(
                self.room_group_name,
                { 'type': 'user_left_notify' }
                )
        
        self.chat = None
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        
    async def user_left_notify(self, event):        
        await self.send(text_data=json.dumps({
            'message_type': MESSAGE_TYPE["USER_LEFT"],
            'message': 'User has left the room.'
        }))
        
    @database_sync_to_async
    def save_message_status(self, msg_type, id ):
        if "MESSAGE_READED" == MESSAGE_TYPE[msg_type]:
            status = "SEEN"
        if "MESSAGE_DELIVERD" == MESSAGE_TYPE[msg_type]:
            status = "DELIVERED"
        msg = Message.objects.get(id=id)
        msg.status=status
        msg.save()
        
    @database_sync_to_async
    def save_text_message(self, message, message_id):
        dt_timestamp = datetime.strptime(message["timestampe"], "%Y-%m-%d %H:%M:%S.%f")
        sender = User.objects.get(id=message["sender"])
        obj = Message.objects.create(
            id=message_id,
            chat=self.chat,
            sender=sender,  
            content=message["content"],
            timestampe=dt_timestamp,
            status="SENT",
        )

    @database_sync_to_async
    def get_chat_obj(self, id):
        return Chat.objects.filter(id=id).first()
