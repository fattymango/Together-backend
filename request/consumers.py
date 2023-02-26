import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth.models import AnonymousUser
class ChatConsumer(WebsocketConsumer):

    def connect(self):
        
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "chat_%s" % self.room_name
        if isinstance(self.scope["user"],AnonymousUser) or self.scope["user"] == "no user":
            self.room_name = "not-authorized"
            self.room_group_name = "chat_%s" % self.room_name
            self.accept()
            self.close(4444)
            
            
        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        user = self.scope["user"]
        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {"type": "chat_message", "message": message,"user":self.scope["user"].email}
        )

    # Receive message from room group
    def chat_message(self, event):
        print(event)
        message = event["message"]

        # Send message to WebSocket
        self.send(text_data=json.dumps({"message": message,"user":event["user"]}))