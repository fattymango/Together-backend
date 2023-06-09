from django.urls import re_path, path

from .consumers import UserConsumer

websocket_urlpatterns = [
	re_path(r'ws/user/(?P<room_name>\w+)/$', UserConsumer.as_asgi()),

]
