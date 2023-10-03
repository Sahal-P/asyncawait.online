from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
import json
from channels.db import database_sync_to_async
from chat.models import UserProfile
from datetime import datetime

NOTIFICATION = {
    "NEW_MESSAGE": "NEW_MESSAGE",
    "READED_MESSAGE": "READED_MESSAGE",
    "DELIVERD_MESSAGE": "DELIVERD_MESSAGE",
    "PERSON_IS_TYPING": "PERSON_IS_TYPING",
    "PERSON_NOT_TYPING": "PERSON_NOT_TYPING",
}


class UserConnection(AsyncWebsocketConsumer):
    
    async def connect(self):
        self.room_group_name = self.scope["url_route"]["kwargs"]["room_name"]
        await self.set_online(self.room_group_name)
        print(self.room_group_name,'user connection --------------------------------------')
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        await self.send(
            json.dumps({"Status": "You are now connected to UserConnection Channel.", "room_name":self.room_group_name})
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        msg = text_data_json["message"]
        action = text_data_json["type"]
        sender = text_data_json["sender"]
        # Handle received data
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "action": action,
                "message": msg,
                "sender": sender,
            },
        )
        
    async def send_notification(self, event):        
        await self.send(
            text_data=json.dumps(
                {
                    "message_type": NOTIFICATION["NEW_MESSAGE"],
                    "content": event['message'],
                    "sender": event['sender'],
                }
            )
        )

    async def chat_message(self, event):
        pass

    async def disconnect(self, close_code):
        await self.set_last_seen(self.room_group_name)
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    @database_sync_to_async
    def set_last_seen(self, id):
        profile = UserProfile.objects.get(user_id=id)
        profile.last_seen = datetime.now()
        profile.is_online = False
        profile.save()
        
    @database_sync_to_async
    def set_online(self, id):
        try:
            profile = UserProfile.objects.get(user_id=id)
            profile.is_online = True
            profile.save()
        except Exception as e:
            print(e)