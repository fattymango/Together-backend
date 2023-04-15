import logging

from rest_framework import permissions
from channels_permissions.permissions import get_request, get_volunteer
from report.models import Report

logger = logging.getLogger(__name__)


class ReportExists(permissions.BasePermission):
	message = 'You cannot create a report, tou have a report already.'

	def has_permission(self, request, view):
		try:
			user = request.user
			get_report(user)
			return False

		except Exception as e:
			return True


class CanCreateReport(permissions.BasePermission):
	message = 'You cannot create a report, you must be assigned to this request.'

	def has_permission(self, request, view):
		try:
			user = request.user

			if user.pk != int(request.data["user"]):
				return False

			req = get_request(view.kwargs.get('pk'))
			assigned_specialNeeds = req.specialNeeds.pk == user.pk
			assigned_volunteer = (req.volunteer != None and req.volunteer.pk == user.pk)

			return assigned_specialNeeds or assigned_volunteer
		except Exception as e:
			return False


class IsAdmin(permissions.BasePermission):
	message = 'You cannot update this report.'

	def has_permission(self, request, view):
		try:
			return request.user.is_just_admin
		except Exception as e:
			return False


def get_report(user) -> Report:
	try:
		return Report.objects.get(user=user)

	except Report.DoesNotExist:
		raise Report.DoesNotExist
