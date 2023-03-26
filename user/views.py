from django.http import HttpResponse
from django.utils.http import urlsafe_base64_decode
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate, get_user_model

from rest_framework.authentication import TokenAuthentication

from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import *

from .token import account_activation_token
from .util import *
from django.utils.encoding import force_str


class UserRegistration(APIView):
	serializer: serializers.ModelSerializer = UserRegistrationSerializer()

	authentication_classes = []
	permission_classes = [AllowAny]

	def post(self, request, format=None):
		data = {}

		serializer = self.serializer(data=request.data)
		if serializer.is_valid(raise_exception=True):
			user = serializer.save()
			serialize_user(data, user)
		else:
			data = serializer.errors
		return Response(data)


class SpecialNeedUserRegistration(UserRegistration):
	serializer = SpecialNeedsRegistrationSerializer


class VolunteerUserRegistration(UserRegistration):
	serializer = VolunteerRegistrationSerializer


class AdminUserRegistration(UserRegistration):
	serializer = AdminRegistrationSerializer


class UserLogin(APIView):
	authentication_classes = []
	permission_classes = []

	def post(self, request):
		context = {}
		username = request.POST.get('username')
		password = request.POST.get('password')
		user = authenticate(email=username, password=password)
		if user:
			serialize_user(context, user)
			context['response'] = 'successfully authenticated'
		else:
			context['response'] = 'Error'
			context['error_message'] = 'Invalid credentials'

		return Response(context)


class SetUserOnline(APIView):
	authentication_classes = [TokenAuthentication]
	permission_classes = [IsAuthenticated]

	def put(self, request):
		context = {}
		user = Token.objects.get(key=request.auth.key).user
		is_online = request.data.get('is_online')
		if user and is_online:

			user.is_online = True if (is_online == "true") else False
			user.save()
			serialize_user(context, user)
			context['response'] = 'successfully changed status'
			context["is_online"] = user.is_online
		elif not is_online:
			context['response'] = 'Error'
			context['error_message'] = 'You must provide a value'
		else:
			context['response'] = 'Error'
			context['error_message'] = 'Invalid credentials'

		return Response(context)


class ActivateUser(APIView):
	authentication_classes = []
	permission_classes = []

	def get(request, *args, **kwargs):
		User = get_user_model()
		uidb64 = kwargs.get("uidb64")
		token = kwargs.get("token")
		print(args, kwargs)
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
