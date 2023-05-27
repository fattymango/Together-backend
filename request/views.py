import logging

from django.conf import settings
from django.core.cache import cache
from rest_framework import generics, views
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from chat.models import ChatRoom
from location.permissions import IsVolunteer
from user.serializers import BaseUserSerializer
from .models import RequestSerializer as CeleryRequestSerializer
from .serializers import RequestSerializer, UpdateRequestSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
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

	def set_volunteer_chat_room(self, request_pk, value):
		room = ChatRoom.objects.get(id=request_pk)
		room.volunteer = value
		room.save()

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

		data = {"response" : "accept",
		        "message"  : "Volunteer has accepted the request",
		        "volunteer": BaseUserSerializer(volunteer).data, }
		if volunteer_location:
			data["location"] = {"latitude" : volunteer_location[0],
			                    "longitude": volunteer_location[1]}
		else:
			data["location"] = {"latitude" : 0,
			                    "longitude": 0}

		send_request_consumer_message(request_pk, data)
		set_volunteer_is_available(volunteer.justID, False)
		self.set_volunteer_chat_room(request_pk, volunteer)
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

		serialized_request = dict(CeleryRequestSerializer(Request.objects.get(id=request_pk)).data)
		send_request_consumer_message(request_pk, {"response": "cancel",
		                                           "message" : "User has cancelled the request, waiting for a new volunteer"})
		task_send_request.delay(serialized_request)
		set_volunteer_is_available(volunteer.justID, True)
		self.set_volunteer_chat_room(request_pk, None)
		return self.partial_update(request, *args, **kwargs)


class FinishRequest(AcceptRequest):
	permission_classes = [IsAuthenticated, IsSpecialNeeds, OwnsRequest, RequestNotFinished]

	def patch(self, request, *args, **kwargs):
		try:
			request.data.update({'is_finished': True})
		except AttributeError:
			request.data._mutable = True
			request.data.update({'is_finished': True})
		send_request_consumer_message(kwargs.get('pk'), {"response": "finish",
		                                                 "message" : "Request is finished."})
		req = Request.objects.get(pk=kwargs.get('pk'))
		if req.volunteer:
			set_volunteer_is_available(req.volunteer.justID, True)
		return self.partial_update(request, *args, **kwargs)


class DeclineRequest(APIView):
	# permission_classes=[IsAuthenticated,IsVolunteer,CanDeclineRequest]
	authentication_classes = [TokenAuthentication]

	def get(self, request, *args, **kwargs):
		volunteer = request.user
		request_pk = kwargs.get('pk')
		try:
			serialized_request = dict(CeleryRequestSerializer(Request.objects.get(id=request_pk)).data)

			task_send_request.delay(serialized_request)
			set_volunteer_is_available(volunteer.justID, True)
			return Response(data={"response": "success"})
		except:
			return Response(data={"response": "Error", "data": "this request does not exist."})


class GetLastRequest(APIView):
	# permission_classes=[IsAuthenticated,IsVolunteer,CanDeclineRequest]
	authentication_classes = [TokenAuthentication]

	def get_request_query(self, request) -> Request:
		return None

	def get_chat_websocket_url(self, pk):
		return None

	def get_request_websocket_url(self, pk):
		return None

	def get(self, request, *args, **kwargs):

		try:

			req = self.get_request_query(request)
			if req == None:
				raise
			serialized_request = dict(CeleryRequestSerializer(req).data)
			serialized_request["request_websocket"] = self.get_request_websocket_url(req.pk)
			serialized_request["chatroom_websocket"] = self.get_chat_websocket_url(req.pk)
			# set_volunteer_is_available(volunteer.justID, False)
			return Response(data={"response": "success", "data": serialized_request})
		except Exception as e:
			logger.error(e)
			return Response(data={"response": "Error", "data": "You do not have any request"})


class SpecialNeedsGetLastRequest(GetLastRequest):
	permission_classes = [IsSpecialNeeds]

	def get_chat_websocket_url(self, pk):
		return generate_websocket(prefix="ws", view_name="chatroom",
		                          request_id=str(pk))

	def get_request_websocket_url(self, pk):
		return generate_websocket(prefix="ws", view_name="request",
		                          volunteer="specialneed",
		                          request_id=str(pk))

	def get_request_query(self, request) -> Request:
		return Request.objects.filter(specialNeeds=request.user).last()


class VolunteerGetLastRequest(GetLastRequest):
	permission_classes = [IsVolunteer]

	def get_chat_websocket_url(self, pk):
		return generate_websocket(prefix="ws", view_name="chatroom",
		                          request_id=str(pk))

	def get_request_websocket_url(self, pk):
		return generate_websocket(prefix="ws", view_name="request",
		                          volunteer="volunteer",
		                          request_id=str(pk))

	def get_request_query(self, request) -> Request:
		return Request.objects.filter(volunteer=request.user).last()
