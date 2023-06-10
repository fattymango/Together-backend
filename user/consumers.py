from asgiref.sync import async_to_sync

from channels_permissions.consumers import PermissionsJsonWebsocketConsumer
from channels_permissions.permissions import NotAnonymousUser
from .permissions import UserOwnsRoom


class UserConsumer(PermissionsJsonWebsocketConsumer):
	permission_classes = [NotAnonymousUser, UserOwnsRoom]

	def connect(self):
		self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
		self.room_group_name = "user%s" % self.room_name

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
	def receive_json(self, content, **kwargs):
		data = content["data"]
		# Send message to room group
		async_to_sync(self.channel_layer.group_send)(
			self.room_group_name, {"type": "chat_message", "data": data}
		)

	# Receive message from room group
	def chat_message(self, event):
		data = event["data"]

		# Send message to WebSocket
		self.send_json(content={"data": data})
