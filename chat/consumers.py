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

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        print(text_data_json)
        message = text_data_json["message"]
        username = text_data_json["username"]
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username
            }
        )

    def chat_message(self, event):
        try:
            print(event)
            message = event['message']
            username = event['username']
            self.send(text_data=json.dumps({
                'message': message,
                'username': username
            }))
        except KeyError:
            pass

    def redirect_to_chat(self, event):
        redirect_url = event['redirect']
        self.send(text_data=json.dumps({'redirect': redirect_url}))


class MatchingConsumer(WebsocketConsumer):
    def connect(self):
        self.room_group_name = 'matching'
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()
        async_to_sync(self.match_users)()

    def disconnect(self, close_code):
        self.channel_layer.group_discard('matching_group', self.channel_name)

    def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            print(text_data_json, "cdcdxsc")
            redirect = text_data_json["redirect"]
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'send_redirect',
                    'redirect': redirect,
                }
            )
        except KeyError:
            pass

    @database_sync_to_async
    def match_users(self):
        user = self.scope['user']
        online_users = User.objects.filter(is_online=True, is_ready=True, in_chat=False).exclude(pk=user.pk)
        matched_users = []
        matched_user = []
        for i in online_users:
            for interest in i.interests:
                if interest in user.interests:
                    matched_users.append(i)
                    break

        if matched_users:
            matched_user = random.choice(matched_users)
        else:
            try:
                matched_user = random.choice(online_users)
            except IndexError:
                self.send(text_data=json.dumps({'error': "No online users available for matching"}))
        if matched_user:
            if user.pk >= matched_user.pk:
                room_name = f"{user.pk}-{matched_user.pk}"
            else:
                room_name = f"{matched_user.pk}-{user.pk}"
            self.send(text_data=json.dumps({'redirect': f'/chat/{room_name}'}))

    def send_redirect(self, event):
        print(event, "eventtttttttt")
        room_name = event['redirect']
        redirect_url = {'redirect': room_name}
        self.send(text_data=json.dumps(redirect_url))
