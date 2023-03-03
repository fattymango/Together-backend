from django.urls import re_path
from .consumers import RequestConsumer

websocket_urlpatterns = [
    re_path(r'ws/request/(?P<room_name>\w+)/$', RequestConsumer.as_asgi()),
]