from channels.exceptions import DenyConnection
from .permissions import BasePermission


class Permissions(object):
	permission_classes = [BasePermission]

	def check_permissions(self):
		try:
			for permission in self.permission_classes:
				if permission(scope=self.scope).validate() != None:
					raise DenyConnection
		except PermissionError:
			raise DenyConnection



