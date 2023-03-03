from django.contrib.auth.models import AnonymousUser

from request.models import Request
from user.models import Volunteer


class BasePermission(object):
	def __init__(self, scope, *args, **kwargs) -> None:
		self.scope = scope

	def has_permission(self, *args, **kwargs) -> bool:
		return True

	def validate(self, *args, **kwargs):
		try:
			if not self.has_permission(*args, **kwargs):
				return PermissionError
		except Exception:
			return RuntimeError
		return None


class NotAnonymousUser(BasePermission):

	def has_permission(self, *args, **kwargs) -> bool:
		try:
			return not isinstance(self.scope["user"],AnonymousUser)
		except Exception:
			return False


class RequestNotAssigned(BasePermission):

	def has_permission(self, *args, **kwargs) -> bool:
		try:
			request = get_request(self.scope["url_route"]["kwargs"]["room_name"])
			usr = get_volunteer(self.scope["user"].pk)

			return (request.volunteer == None or request.volunteer == usr)
		except Exception:
			return False


class VolunteerValidated(BasePermission):

	def has_permission(self, *args, **kwargs) -> bool:
		try:
			usr = get_volunteer(self.scope["user"].pk)
			return usr.is_validated == True
		except Exception:
			return False


def get_request(pk) -> Request:
	try:
		return Request.objects.get(id=pk)

	except Request.DoesNotExist:
		raise Request.DoesNotExist


def get_volunteer(pk) -> Volunteer:
	try:
		return Volunteer.objects.get(id=pk)
	except Volunteer.DoesNotExist:
		raise Volunteer.DoesNotExist
	except Exception:
		raise RuntimeError("Can't resolve KeyWord user")
