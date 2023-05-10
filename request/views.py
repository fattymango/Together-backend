import logging

from django.conf import settings
from django.core.cache import cache
from rest_framework import generics, views
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from user.serializers import BaseUserSerializer
from .models import clean_fields
from .serializers import RequestSerializer, UpdateRequestSerializer
from rest_framework.response import Response
from rest_framework import status
from django.contrib.sites.shortcuts import get_current_site
from .permissions import *
from .util import send_request_consumer_message, set_volunteer_is_available, generate_websocket
from .tasks import task_send_request

logger = logging.getLogger(__name__)


# Create your views here.
class CreateRequest(generics.CreateAPIView):
	queryset = Request.objects.all()
	serializer_class = RequestSerializer
	permission_classes = [IsAuthenticated, IsSpecialNeeds, NoOpenRequest]
	authentication_classes = [TokenAuthentication]

	def create(self, request, *args, **kwargs):
		try:

			try:
				request.data.update({'specialNeeds': request.user.id})
			except AttributeError:
				request.data._mutable = True
				request.data.update({'specialNeeds': request.user.id})
			logger.error(request.user)
			response = super().create(request, *args, **kwargs)
			logger.error("hello2")
			response.data["request_websocket"] = generate_websocket(prefix="ws", view_name="request",
			                                                        specialneed="specialneed",
			                                                        request_id=str(response.data["id"]))
			response.data["chatroom_websocket"] = generate_websocket(prefix="ws", view_name="chatroom",
			                                                         request_id=str(response.data["id"]))
			return response
		except Exception:
			logging.critical(Exception, exc_info=True)
			return Response(data={"error": "error has occurred, please make sure the credentials are correct."},
			                status=status.HTTP_400_BAD_REQUEST)


class AcceptRequest(generics.UpdateAPIView):
	queryset = Request.objects.all()
	serializer_class = UpdateRequestSerializer
	permission_classes = [IsAuthenticated, CanAcceptRequestPermission, RequestNotFinished]
	authentication_classes = [TokenAuthentication]

	def put(self, request, *args, **kwargs):
		return self.patch(request, *args, **kwargs)

	def patch(self, request, *args, **kwargs):
		volunteer = request.user
		request_pk = kwargs.get('pk')
		volunteer_location = cache.get(
			settings.CACHE_PREFIXES["LOCATION"]["VOLUNTEER"].replace("*", str(volunteer.justID)))

		try:
			request.data.update({'volunteer': volunteer.pk})
		except AttributeError:
			request.data._mutable = True
			request.data.update({'volunteer': volunteer.pk})

		data = {"response"      : "success",
		        "message"       : "Volunteer has accepted the request",
		        "volunteer_name": BaseUserSerializer(volunteer), }
		if volunteer_location:
			data["location"] = {"latitude" : volunteer_location[0],
			                    "longitude": volunteer_location[1]}

		send_request_consumer_message(request_pk, data)
		set_volunteer_is_available(volunteer.justID, False)

		return self.partial_update(request, *args, **kwargs)


class CancelRequest(AcceptRequest):
	permission_classes = [IsAuthenticated, CanCancelRequestPermission, RequestNotFinished]

	def patch(self, request, *args, **kwargs):
		try:
			request.data.update({'volunteer': None})
		except AttributeError:
			request.data._mutable = True
			request.data.update({'volunteer': None})
		volunteer = request.user
		request_pk = kwargs.get('pk')

		serialized_request = clean_fields(Request.objects.get(id=request_pk), fields=["_state", "date_created", "is_finished"])
		send_request_consumer_message(request_pk, "User has cancelled the request, waiting for a new volunteer")
		task_send_request.delay(serialized_request)
		set_volunteer_is_available(volunteer.justID, True)
		return self.partial_update(request, *args, **kwargs)


class FinishRequest(AcceptRequest):
	permission_classes = [IsAuthenticated, IsSpecialNeeds, OwnsRequest, RequestNotFinished]

	def patch(self, request, *args, **kwargs):
		try:
			request.data.update({'is_finished': True})
		except AttributeError:
			request.data._mutable = True
			request.data.update({'is_finished': True})
		send_request_consumer_message(kwargs.get('pk'), "Request has been finished.")
		return self.partial_update(request, *args, **kwargs)
