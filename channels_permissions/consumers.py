import logging

from channels.exceptions import DenyConnection
from channels.generic.websocket import WebsocketConsumer, JsonWebsocketConsumer

from .mixins import PermissionsMixin

logger = logging.getLogger(__name__)


class PermissionsMixinWebsocketConsumer(WebsocketConsumer, PermissionsMixin):
	permission_classes = []

	def websocket_connect(self, message):
		try:
			self.check_permissions()
		except DenyConnection:
			self.close()
		super().websocket_connect(message)


class PermissionsMixinJsonWebsocketConsumer(JsonWebsocketConsumer, PermissionsMixin):
	permission_classes = []

	def websocket_connect(self, message):
		try:
			self.check_permissions()
		except DenyConnection:
			self.close()
		super().websocket_connect(message)
