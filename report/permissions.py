import logging

from rest_framework import permissions
from channels_permissions.permissions import get_request, get_volunteer
from report.models import Report
from request.models import Request

logger = logging.getLogger(__name__)


class ReportExists(permissions.BasePermission):
	message = 'You cannot create a report, you have a report already.'

	def has_permission(self, request, view):
		if request.data.get("request", None) == None:
			return True
		try:
			get_report(request.data["request"])
			return False

		except Exception as e:
			return True


class CanCreateReport(permissions.BasePermission):
	message = 'You cannot create a report, you do not own this request.'

	def has_permission(self, request, view):
		if request.data.get("request", None) == None:
			return True
		try:
			user = request.user

			req = get_request(int(request.data["request"]))

			return req.specialNeeds.pk == user.pk
		except Exception as e:
			return False


class IsAdmin(permissions.BasePermission):
	message = 'You cannot update this report.'

	def has_permission(self, request, view):
		try:
			return request.user.is_just_admin
		except Exception as e:
			return False


def get_report(pk):
	try:
		return Report.objects.get(request=int(pk))

	except Report.DoesNotExist:
		raise Report.DoesNotExist
