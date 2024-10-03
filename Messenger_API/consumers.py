# consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from datetime import datetime
from Users.models import UserModel
from .models import MessageModel
from django.db.utils import IntegrityError

# Dictionary to store unsent messages for users
unsent_messages = {}

# Dictionary to keep track of connected users and their channel names
connected_users = {}

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.receiver_profile_id = self.scope['url_route']['kwargs']['profile_id']
        self.receiver_user = await self.get_user_by_profile_id(self.receiver_profile_id)

        if self.receiver_user:
            self.sender_user = self.scope['user']
            connected_users[self.sender_user.profile_id] = self.channel_name
            await self.accept()

            # Check if there are any unsent messages for the receiver and send them
            if self.sender_user.profile_id in unsent_messages:
                for message in unsent_messages[self.sender_user.profile_id]:
                    await self.send(text_data=json.dumps(message))
                # Clear the unsent messages for this receiver after sending
                del unsent_messages[self.sender_user.profile_id]
        else:
            await self.send(text_data=json.dumps({'error': 'User not found.'}))
            await self.close()

    async def disconnect(self, close_code):
        if self.sender_user and self.sender_user.profile_id in connected_users:
            del connected_users[self.sender_user.profile_id]
        pass

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            content = text_data_json.get('message', '')

            if not content.strip():
                await self.send(text_data=json.dumps({'error': 'Message cannot be empty.'}))
                return

            sender = self.scope['user']

            if self.receiver_user:
                try:
                    # Save the message to the database
                    message = await self.save_message(sender, self.receiver_user, content)
                    await self.send_message_to_receiver(message, self.receiver_user.profile_id)
                    
                    # Send a confirmation to the sender without the detailed report
                    await self.send(text_data=json.dumps({'status': 'Message sent successfully.'}))
                except IntegrityError:
                    await self.send(text_data=json.dumps({'error': 'Failed to save message.'}))
            else:
                await self.send(text_data=json.dumps({'error': 'Receiver not found.'}))
                await self.close()

        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({'error': 'Invalid message format.'}))

    @database_sync_to_async
    def get_user_by_profile_id(self, profile_id):
        try:
            return UserModel.objects.get(profile_id=profile_id)
        except UserModel.DoesNotExist:
            return None

    @database_sync_to_async
    def save_message(self, sender, receiver, content):
        return MessageModel.objects.create(
            sender=sender,
            receiver=receiver,
            content=content,
            timestamp=datetime.now()
        )

    async def send_message_to_receiver(self, message, receiver_profile_id):
        message_data = {
            'sender': message.sender.profile_id,
            'receiver': receiver_profile_id,
            'content': message.content,
            'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }

        if receiver_profile_id in connected_users:
            receiver_channel = connected_users[receiver_profile_id]
            await self.channel_layer.send(
                receiver_channel,
                {
                    'type': 'chat_message',
                    'message': message_data,
                }
            )
        else:
            # Store unsent message in memory for later delivery
            if receiver_profile_id not in unsent_messages:
                unsent_messages[receiver_profile_id] = []
            unsent_messages[receiver_profile_id].append(message_data)

    async def chat_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps(message))
