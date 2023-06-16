from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
import json
from datetime import datetime

MESSAGE_MAX_LENGTH = 100

MESSAGE_ERROR_TYPE = {
    "MESSAGE_OUT_OF_LENGTH": 'MESSAGE_OUT_OF_LENGTH',
    "UN_AUTHENTICATED": 'UN_AUTHENTICATED',
    "INVALID_MESSAGE": 'INVALID_MESSAGE',
}

MESSAGE_TYPE = {
    "WENT_ONLINE": 'WENT_ONLINE',
    "WENT_OFFLINE": 'WENT_OFFLINE',
    "IS_TYPING": 'IS_TYPING',
    "NOT_TYPING": 'NOT_TYPING',
    "MESSAGE_COUNTER": 'MESSAGE_COUNTER',
    "OVERALL_MESSAGE_COUNTER": 'OVERALL_MESSAGE_COUNTER',
    "TEXT_MESSAGE": 'TEXT_MESSAGE',
    "MESSAGE_READ": 'MESSAGE_READ',
    "ALL_MESSAGE_READ": 'ALL_MESSAGE_READ',
    "ERROR_OCCURED": 'ERROR_OCCURED'    
}

class ChatConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        self.room_group_name = self.scope['url_route']['kwargs']['room_name']
        print(self.channel_name)
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name)
        await self.accept()
        await self.send(json.dumps({"status":f"connected [{self.room_group_name}]"}))

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        msg = text_data_json['message']
        action = text_data_json['type']
        sender = text_data_json['sender']
        # Handle received data
        print(text_data_json,'-----------json')
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'action': action,
                'message': msg,
                'sender': sender
            }
        )
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'msg_type': MESSAGE_TYPE['TEXT_MESSAGE'],
            'message': event['message'],
            'sender': event['sender'],
            'timestampe': str(datetime.now()),
        }))
        
    async def disconnect(self, code):
        # self.set_offline()
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )