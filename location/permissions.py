from channels_permissions.permissions import get_volunteer, get_request
from request.models import Request
from user.models import Volunteer
from request.permissions import IsSpecialNeeds
from rest_framework import permissions


class IsSpecialNeeds(IsSpecialNeeds):
	message = 'You must be a Special Needs user to update your location'


class IsVolunteer(permissions.BasePermission):
	message = 'You must be a Volunteer user to update your location'

	def has_permission(self, request, view):
		try:
			user = get_volunteer(request.user.pk)
			if not user:
				return False
		except Exception:
			return False
		return True


class CanGetVolunteersLocation(permissions.BasePermission):
	message = 'You must can not get the location of this volunteer'

	def has_permission(self, request, view):
		try:
			print(view.kwargs.get("pk"))
			Request.objects.get(specialNeeds=request.user,
			                    volunteer=Volunteer.objects.get(justID=view.kwargs.get("pk")), is_finished=False)

		except Exception:
			return False
		return True
