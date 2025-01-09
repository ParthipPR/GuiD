# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from datetime import datetime

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        self.user = self.scope["user"]

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        timestamp = datetime.now().strftime("%H:%M")
        username = self.user.username if self.user.is_authenticated else "Anonymous"

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username,
                'timestamp': timestamp,
                'sender': self.channel_name
            }
        )

    async def chat_message(self, event):
        if event['sender'] != self.channel_name:
            await self.send(text_data=json.dumps({
                'message': event['message'],
                'username': event['username'],
                'timestamp': event['timestamp']
            }))