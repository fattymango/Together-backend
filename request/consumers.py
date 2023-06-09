from asgiref.sync import async_to_sync

from channels_permissions.consumers import PermissionsMixinJsonWebsocketConsumer
from channels_permissions.permissions import *


class RequestConsumer(PermissionsMixinJsonWebsocketConsumer):
	permission_classes = []

	def connect(self):
		self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
		self.room_group_name = "request%s" % self.room_name
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
	def receive_json(self, content, **kwargs):
		data = content["data"]
		# Send message to room group
		async_to_sync(self.channel_layer.group_send)(
			self.room_group_name, {"type": "chat_message", "data": data, "user": self.scope["user"].email}
		)

	# Receive message from room group
	def chat_message(self, event):
		data = event["data"]

		# Send message to WebSocket
		self.send_json(content={"data": data})


class VolunteerRequestConsumer(RequestConsumer):
	permission_classes = [NotAnonymousUser, IsVolunteer, VolunteerValidated, AssignedToRequest]


class SpecialNeedsRequestConsumer(RequestConsumer):
	permission_classes = [NotAnonymousUser, IsSpecialNeeds, OwnsRequest]
