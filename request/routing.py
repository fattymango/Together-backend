from django.urls import re_path
from .consumers import RequestConsumer,VolunteerRequestConsumer,SpecialNeedsRequestConsumer

websocket_urlpatterns = [
    re_path(r'ws/request/specialneed/(?P<room_name>\w+)/$', SpecialNeedsRequestConsumer.as_asgi()),
    re_path(r'ws/request/volunteer/(?P<room_name>\w+)/$', VolunteerRequestConsumer.as_asgi()),
]