from channels_permissions.permissions import BasePermission


class UserOwnsRoom(BasePermission):
	def has_permission(self, *args, **kwargs) -> bool:
		try:
			return int(self.scope["user"].justID) == int(self.scope["url_route"]["kwargs"]["room_name"])
		except Exception:
			return False