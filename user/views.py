from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import authenticate
from django.utils.encoding import force_str

from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView
from rest_framework.generics import UpdateAPIView, RetrieveAPIView
from rest_framework.response import Response

from location.permissions import IsVolunteer, IsSpecialNeeds
from report.permissions import IsAdmin
from request.util import set_volunteer_is_available

from .serializers import *
from .util import *

import logging

logger = logging.getLogger(__name__)


class UserRegistration(APIView):
	serializer: serializers.ModelSerializer = UserRegistrationSerializer

	authentication_classes = []
	permission_classes = [AllowAny]

	def post(self, request, format=None):
		data = {}


		serializer = self.serializer(data=request.data)
		if serializer.is_valid():
			user = serializer.save()

			data = BaseUserSerializer(user).data
			data['response'] = 'successfully authenticated'
		else:

			data['response'] = 'Error'
			data['error_message'] = serializer.errors
		return Response(data)


class test(RetrieveAPIView):
	queryset = BaseUser.objects.all()
	authentication_classes = []
	permission_classes = []
	serializer_class = BaseUserSerializer


class UserLogin(APIView):
	authentication_classes = []
	permission_classes = []

	def post(self, request):
		context = {}
		username = request.POST.get('username')
		password = request.POST.get('password')

		user = authenticate(username=username, password=password)

		if user:
			context = BaseUserSerializer(user).data
			context['response'] = 'successfully authenticated'
		else:
			context['response'] = 'Error'
			context['error_message'] = 'Invalid credentials'

		return Response(context)


class SetUserOnline(APIView):
	authentication_classes = [TokenAuthentication]
	permission_classes = []
	prefix = None

	def delete_location(self, user):
		key = self.prefix.replace("*", (str(user.justID)))
		cache.delete(key)

	def set_online(self, user, is_online):
		user.is_online = is_online
		user.save()


	def get_is_online(self,request):
		return True if (request.data.get('is_online') == "true") else False
	def put(self, request):
		context = {}

		try:
			user = request.user
			is_online = self.get_is_online(request)
			if not is_online:
				self.delete_location(user)
			self.set_online(user, is_online)

			context = BaseUserSerializer(user).data
			context['response'] = 'successfully changed status'
			context["is_online"] = user.is_online

		except Exception as e:
			context['response'] = 'Error'
			context['error_message'] = 'Invalid credentials'

		return Response(context)


class SetVolunteerOnline(SetUserOnline):
	permission_classes = [IsAuthenticated, IsVolunteer]
	prefix = settings.CACHE_PREFIXES["LOCATION"]["VOLUNTEER"]

	def set_available(self, justID, value):
		set_volunteer_is_available(justID, value)

	def put(self, request):
		user = request.user
		is_online = self.get_is_online(request)
		if is_online:
			self.set_available(user.justID, is_online)
		return super().put(request)


class SetSpecialNeedsOnline(SetUserOnline):
	permission_classes = [IsAuthenticated, IsSpecialNeeds]
	prefix = settings.CACHE_PREFIXES["LOCATION"]["SPECIALNEEDS"]


class ActivateUser(APIView):
	authentication_classes = []
	permission_classes = []

	def get(self, request, *args, **kwargs):
		User = get_user_model()
		uidb64 = kwargs.get("uidb64")
		token = kwargs.get("token")
		try:
			uid = force_str(urlsafe_base64_decode(uidb64))
			user = User.objects.get(pk=uid)
		except(TypeError, ValueError, OverflowError, User.DoesNotExist):
			user = None
		if user is not None and account_activation_token.check_token(user, token):
			user.is_active = True
			user.save()
			return HttpResponse('Thank you for your email confirmation. Now you can login your account.')
		else:
			return HttpResponse('Activation link is invalid!')


class GetUserInfo(APIView):
	authentication_classes = [TokenAuthentication]

	def get(self, request, format=None):
		context = {}
		try:
			context = BaseUserSerializer(request.user).data
			context["response"] = "Data retrieved successfully."
		except Exception:
			context["response"] = "Error"
		return Response(context)


class ValidateVolunteer(UpdateAPIView):
	queryset = Volunteer.objects.all()
	serializer_class = UpdateVolunteerSerializer
	permission_classes = [IsAuthenticated, IsAdmin]
	authentication_classes = [TokenAuthentication]
