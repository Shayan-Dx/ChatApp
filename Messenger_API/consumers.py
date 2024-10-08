import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone  # Using timezone.now() instead of datetime.now()
from Users.models import UserModel
from .models import MessageModel
from django.db.utils import IntegrityError
from django.db.models import Q

# A dictionary to keep track of connected users and their channel names
connected_users = {}

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.receiver_profile_id = self.scope['url_route']['kwargs']['profile_id']
        self.receiver_user = await self.get_user_by_profile_id(self.receiver_profile_id)
        
        if self.receiver_user:
            self.sender_user = self.scope['user']
            connected_users[self.sender_user.profile_id] = self.channel_name
            await self.accept()

            # Send chat history to the sender upon connection
            chat_history = await self.get_chat_history(self.sender_user, self.receiver_user)
            await self.send(text_data=json.dumps({'chat_history': chat_history}))
        else:
            await self.send(text_data=json.dumps({'error': 'User not found.'}))
            await self.close()  # Ensure proper closing if user is not found

    async def disconnect(self, close_code):
        if self.sender_user and self.sender_user.profile_id in connected_users:
            # Ensure proper cleanup when a user disconnects
            del connected_users[self.sender_user.profile_id]

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
                    
                    # Send a confirmation to the sender
                    await self.send(text_data=json.dumps({'status': 'Message sent successfully.'}))
                except IntegrityError:
                    await self.send(text_data=json.dumps({'error': 'Failed to save message.'}))
                except Exception as e:
                    await self.send(text_data=json.dumps({'error': f'Unexpected error: {str(e)}'}))
            else:
                await self.send(text_data=json.dumps({'error': 'Receiver not found.'}))
                await self.close()  # Ensure proper closing if receiver is not found

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
            timestamp=timezone.now()  # Use timezone-aware timestamp
        )

    @database_sync_to_async
    def get_chat_history(self, sender, receiver):
        # Fetch the chat history between the sender and receiver
        messages = MessageModel.objects.filter(
            (Q(sender=sender) & Q(receiver=receiver)) | (Q(sender=receiver) & Q(receiver=sender))
        ).order_by('timestamp')

        return [
            {
                'sender': message.sender.profile_id,
                'receiver': message.receiver.profile_id,
                'content': message.content,
                'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            } for message in messages
        ]

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

    async def chat_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps(message))
