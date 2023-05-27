from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path("chat/<str:room_name>", consumers.ChatConsumer.as_asgi()),
    path("matching/", consumers.MatchingConsumer.as_asgi()),
]
