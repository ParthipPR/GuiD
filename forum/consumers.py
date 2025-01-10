from channels.generic.websocket import AsyncWebsocketConsumer
import json
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name.replace(" ", "_")}'  # Replace spaces with underscores

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

    @database_sync_to_async
    def save_message(self, message, username):
        try:
            # Move imports here to avoid circular imports
            User = get_user_model()
            from forum.models import ChatRoom, ChatMessage  # Adjust 'forum' to your app name

            user = User.objects.get(username=username)
            room = ChatRoom.objects.get(name=self.room_name)
            message = ChatMessage.objects.create(
                room=room,
                author=user,
                content=message
            )
            return message
        except Exception as e:
            print(f"Error saving message: {e}")
            return None

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        username = text_data_json['username']
        timestamp = text_data_json['timestamp']

        # Save message to database
        await self.save_message(message, username)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username,
                'timestamp': timestamp
            }
        )

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'username': event['username'],
            'timestamp': event['timestamp']
        }))