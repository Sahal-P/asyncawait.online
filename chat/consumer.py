from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
import json
from datetime import datetime
from .models import Chat, MediaMessage, Message, UserProfile
from account.models import User
import uuid
from account.uuid_serializer import UUID, UUIDEncoder

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
    "MESSAGE_READ": "MESSAGE_READ",
    "ALL_MESSAGE_READ": "ALL_MESSAGE_READ",
    "MESSAGE_DELETE_FOR_ME": "MESSAGE_DELETE_FOR_ME",
    "MESSAGE_DELETE_FOR_EVERYONE": "MESSAGE_DELETE_FOR_EVERYONE",
    "ERROR_OCCURED": "ERROR_OCCURED",
}


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = self.scope["url_route"]["kwargs"]["room_name"]
        print(self.channel_name)
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        self.chat = await self.get_chat_obj(self.room_group_name)
        await self.send(json.dumps({"status": f"connected [{self.room_group_name}]"}))

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        content = text_data_json["content"]
        msg_type = text_data_json["type"]
        sender = text_data_json["sender"]
        timestampe = text_data_json["timestampe"]
        # Handle received data
        if msg_type == MESSAGE_TYPE["TEXT_MESSAGE"]:
            message_id = uuid.uuid4()
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "content": content,
                    "sender": sender,
                    "timestampe": timestampe,
                    "id": str(message_id),
                },
            )
            await self.save_text_message(text_data_json, message_id)

    async def chat_message(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "message_type": MESSAGE_TYPE["TEXT_MESSAGE"],
                    "id": event["id"],
                    "content": event["content"],
                    "sender": event["sender"],
                    "timestampe": event["timestampe"],
                    "status": "SENT",
                }
            )
        )

    async def disconnect(self, code):
        # self.set_offline()
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

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
