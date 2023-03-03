
from rest_framework import generics, views
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from .serializers import RequestSerializer, UpdateRequestSerializer
from rest_framework.response import Response
from rest_framework import status
from django.contrib.sites.shortcuts import get_current_site
from .permissions import *



# Create your views here.
class CreateRequest(generics.CreateAPIView):
	queryset = Request.objects.all()
	serializer_class = RequestSerializer
	permission_classes = [IsAuthenticated,IsSpecialNeeds,NoOpenRequest]
	authentication_classes = [TokenAuthentication]

	def create(self, request, *args, **kwargs):
		try:

			try:
				request.data.update({'specialNeeds': request.user.pk})
			except AttributeError:
				request.data._mutable = True
				request.data.update({'specialNeeds': request.user.pk})


			response = super().create(request, *args, **kwargs)

			response.data["websocket_url"] = ''.join(
				['ws://', get_current_site(request).domain, "/ws/request/", str(response.data["id"]), "/"])
			return response
		except Exception:
			return Response(data={"error": "error has occurred, please make sure the credentials are correct."},
			                status=status.HTTP_400_BAD_REQUEST)


class AcceptRequest(generics.UpdateAPIView):
	queryset = Request.objects.all()
	serializer_class = UpdateRequestSerializer
	permission_classes = [IsAuthenticated, CanAssignRequestPermission]
	authentication_classes = [TokenAuthentication]

	def put(self, request, *args, **kwargs):
		return self.patch(request, *args, **kwargs)

	def patch(self, request, *args, **kwargs):
		try:
			request.data.update({'volunteer': request.user.pk})
		except AttributeError:
			request.data._mutable = True
			request.data.update({'volunteer': request.user.pk})

		return self.partial_update(request, *args, **kwargs)


class CancelRequest(AcceptRequest):
	permission_classes = [IsAuthenticated, CanCancelRequestPermission]

	def patch(self, request, *args, **kwargs):
		try:
			request.data.update({'volunteer': None})
		except AttributeError:
			request.data._mutable = True
			request.data.update({'volunteer': None})

		return self.partial_update(request, *args, **kwargs)


class FinishRequest(AcceptRequest):
	permission_classes = [IsAuthenticated,IsSpecialNeeds, OwnsRequest]

	def patch(self, request, *args, **kwargs):
		try:
			request.data.update({'is_finished': True})
		except AttributeError:
			request.data._mutable = True
			request.data.update({'is_finished': True})

		return self.partial_update(request, *args, **kwargs)


