from django.urls import re_path
from .consumers import ChatRoomConsumer

websocket_urlpatterns = [
    re_path(r'ws/chatroom/(?P<room_name>\w+)/$', ChatRoomConsumer.as_asgi()),

]