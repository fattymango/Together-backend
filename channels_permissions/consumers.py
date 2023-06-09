import logging

from channels.consumer import AsyncConsumer
from channels.exceptions import DenyConnection
from channels.generic.websocket import WebsocketConsumer, JsonWebsocketConsumer

from .permissions import BasePermission, FalseBasePermission

logger = logging.getLogger(__name__)


class Permissions(object):
	permission_classes = [BasePermission]

	def check_permissions(self):
		try:
			for permission in self.permission_classes:
				if permission(scope=self.scope).validate() != None:
					# logger.error(type(permission(scope=self.scope)))
					raise DenyConnection

		except PermissionError:
			raise DenyConnection


class PermissionsWebsocketConsumer(WebsocketConsumer, Permissions):
	permission_classes = []

	def websocket_connect(self, message):
		try:
			self.check_permissions()
		except DenyConnection:
			self.close()
		super().websocket_connect(message)


class PermissionsJsonWebsocketConsumer(JsonWebsocketConsumer, Permissions):
	permission_classes = []

	def websocket_connect(self, message):
		try:
			self.check_permissions()
		except DenyConnection:
			self.close()
		super().websocket_connect(message)
