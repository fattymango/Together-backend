from channels.exceptions import DenyConnection

from channels_permissions.permissions import BasePermission


class PermissionsMixin(object):
	permission_classes = [BasePermission]

	def check_permissions(self):
		try:
			for permission in self.permission_classes:
				if permission(scope=self.scope).validate() != None:
					# logger.error(type(permission(scope=self.scope)))
					raise DenyConnection

		except PermissionError:
			raise DenyConnection
