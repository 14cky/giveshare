# give/consumers.py
import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        logger.info(f'Connecting to room: {self.room_name}')

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        user = self.scope["user"]
        await self.set_user_status(user, is_online=True)
        await self.broadcast_user_status(user, 'online')

    async def disconnect(self, close_code):
        user = self.scope["user"]
        await self.set_user_status(user, is_online=False)
        await self.broadcast_user_status(user, 'offline')

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')

        if message_type == 'chat_message':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': data['message'],
                }
            )
        elif message_type == 'typing':
            await self.set_user_typing(self.scope["user"], True)
            await self.broadcast_user_status(self.scope["user"], 'typing')
        elif message_type == 'stop_typing':
            await self.set_user_typing(self.scope["user"], False)
            await self.broadcast_user_status(self.scope["user"], 'stop_typing')

    async def chat_message(self, event):
        message = event['message']

        await self.send(text_data=json.dumps({
            'message': message
        }))

    async def user_status(self, event):
        status = event['status']
        user_id = event['user_id']
        timestamp = event['timestamp']

        await self.send(text_data=json.dumps({
            'type': 'user_status',
            'status': status,
            'user_id': user_id,
            'timestamp': timestamp
        }))

    @database_sync_to_async
    def set_user_status(self, user, is_online):
        user.profile.is_online = is_online
        user.profile.last_seen = timezone.now()
        user.profile.save()
        print(f"Set user {user.username} status to {'online' if is_online else 'offline'} at {user.profile.last_seen}")

    @database_sync_to_async
    def set_user_typing(self, user, is_typing):
        user.profile.is_typing = is_typing
        user.profile.save()

    async def broadcast_user_status(self, user, status):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_status',
                'status': status,
                'user_id': user.id,
                'timestamp': timezone.now().isoformat()
            }
        )
        print(f"Broadcasting user {user.username} status {status}")
