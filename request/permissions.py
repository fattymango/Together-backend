from rest_framework import permissions
from channels_permissions.permissions import get_request, get_volunteer
from user.models import SpecialNeed, Volunteer
from .models import Request


class CanAssignRequestPermission(permissions.BasePermission):
	message = 'You cannot accept this request.'

	def has_permission(self, request, view):
		try:
			user = get_volunteer(request.user.pk)
			req = get_request(view.kwargs.get('pk'))
			return req.volunteer == None or req.volunteer == user
		except Exception as e:
			return False


class CanCancelRequestPermission(permissions.BasePermission):
	message = 'You cannot cancel this request.'

	def has_permission(self, request, view):
		try:

			user = get_volunteer(request.user.pk)
			req = get_request(view.kwargs.get('pk'))
			if req.volunteer != user:
				return False
		except Exception:
			return False
		return True


class IsSpecialNeeds(permissions.BasePermission):
	message = 'You must be a Special Needs user to create a request.'

	def has_permission(self, request, view):
		try:
			user = get_specialneeds(request.user.pk)
			if not user:
				return False
		except Exception:
			return False
		return True


class NoOpenRequest(permissions.BasePermission):
	message = 'You cannot create this request, you have a current request.'

	def has_permission(self, request, view):
		try:
			req = get_user_request(request.user.pk)
			if not req:
				return True
			else:
				return req.is_finished
		except Exception:

			return False


class OwnsRequest(permissions.BasePermission):
	message = 'You do not own this request.'

	def has_permission(self, request, view):
		try:
			req = get_request(view.kwargs.get('pk'))
			print(req.specialNeeds, request.user.pk)
			return req.specialNeeds.pk == request.user.pk
		except Exception:

			return False


class RequestNotFinished(permissions.BasePermission):
	message = 'This Request is finished.'

	def has_permission(self, request, view):
		try:
			req = get_request(view.kwargs.get('pk'))
			return not req.is_finished
		except Exception:

			return False


def get_user_request(pk) -> Request:
	try:
		return Request.objects.filter(specialNeeds=pk).last()

	except Request.DoesNotExist:
		raise Request.DoesNotExist


def get_specialneeds(pk) -> SpecialNeed:
	try:
		return SpecialNeed.objects.get(id=pk)

	except SpecialNeed.DoesNotExist:
		raise SpecialNeed.DoesNotExist
