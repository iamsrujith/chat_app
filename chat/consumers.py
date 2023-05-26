import json
import random

from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from channels.generic.websocket import WebsocketConsumer

from chat.models import User


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "chat_%s" % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )

        self.accept()
        # Match users based on interests
        self.match_users()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    def receive(self, text_data):
        # Handle incoming message
        text_data_json = json.loads(text_data)
        print(text_data_json)
        message = text_data_json["message"]
        username = text_data_json["username"]
        # self.send(text_data=json.dumps({'message': message,
        #                                 'username': username}))

        # Send the message to the chat room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username
            }
        )

    def chat_message(self, event):
        # Send the message to the WebSocket
        message = event['message']
        username = event['username']
        # Send the message to the WebSocket
        self.send(text_data=json.dumps({
            'message': message,
            'username': username
        }))
        # self.send(text_data=json.dumps({'message': message}))

    @database_sync_to_async
    def match_users(self):
        user = self.scope['user']
        online_users = User.objects.filter(is_online=True).exclude(pk=user.pk)
        matched_users = online_users.filter(interests__in=user.interests.all())

        if matched_users.exists():
            matched_user = random.choice(matched_users)
        else:
            matched_user = random.choice(online_users)

        # Create a chat room name based on user IDs
        room_name = f"{user.pk}-{matched_user.pk}"
        print(room_name)

        # Redirect the users to the chat room
        self.send(text_data=json.dumps({'redirect': f'/chat/{room_name}'}))
