import logging

from django.contrib.auth.models import AnonymousUser

from chat.models import ChatRoom
from request.models import Request
from user.models import Volunteer,SpecialNeed

logger = logging.getLogger(__name__)
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


class AssignedToRequest(BasePermission):

	def has_permission(self, *args, **kwargs) -> bool:
		try:
			request = get_request(self.scope["url_route"]["kwargs"]["room_name"])
			usr = get_volunteer(self.scope["user"].pk)

			return request.volunteer == usr
		except Exception:
			return False


class VolunteerValidated(BasePermission):

	def has_permission(self, *args, **kwargs) -> bool:
		try:
			usr = get_volunteer(self.scope["user"].pk)
			return usr.is_validated == True
		except Exception:
			return False



class IsVolunteer(BasePermission):

	def has_permission(self, *args, **kwargs) -> bool:
		try:
			user = get_volunteer(self.scope["user"].pk)
			return isinstance(user, Volunteer)
		except Exception:
			return False


class IsSpecialNeeds(BasePermission):

	def has_permission(self, *args, **kwargs) -> bool:
		try:
			user = get_specialneed(self.scope["user"].pk)
			return isinstance(user,SpecialNeed)
		except Exception:
			return False


class OwnsRequest(BasePermission):

	def has_permission(self, *args, **kwargs) -> bool:
		try:
			req = get_request(self.scope["url_route"]["kwargs"]["room_name"])

			return req.specialNeeds.pk == self.scope["user"].pk
		except Exception:
			return False




class CanAccessChatRoom(BasePermission):

	def has_permission(self, *args, **kwargs) -> bool:
		try:
			chat_room = get_chat_room(self.scope["url_route"]["kwargs"]["room_name"])
			logger.error(chat_room)
			user = self.scope["user"]
			return chat_room.specialNeeds == user or chat_room.volunteer == user
		except Exception:
			return False

def get_chat_room(pk)->ChatRoom:
	try:
		return ChatRoom.objects.get(request=pk)

	except ChatRoom.DoesNotExist:
		logger.error("a7a")
		raise ChatRoom.DoesNotExist

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
		raise RuntimeError()

def get_specialneed(pk) -> Volunteer:
	try:
		return SpecialNeed.objects.get(id=pk)
	except SpecialNeed.DoesNotExist:
		raise SpecialNeed.DoesNotExist
	except Exception:
		raise RuntimeError()