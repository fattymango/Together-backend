from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.generics import UpdateAPIView
from django.contrib.auth import authenticate
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication

from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import get_serializer
from .models import *
from .util import *

class RegisterUser(APIView):
    def __init__(self,model, **kwargs) -> None:
        self._model = model
        super().__init__(**kwargs)
    authentication_classes = []
    permission_classes = []

    def post(self, request, format=None):
        
        data = {}
        email = request.data.get('email', '0').lower()
        if email_exists(email):
            data['error_message'] = 'That email is already in use.'
            data['response'] = 'Error'
            return Response(data)

        justID = request.data.get('justID', '0')
        if justID_exists(justID):
            data['error_message'] = 'That justID is already in use.'
            data['response'] = 'Error'
            return Response(data)

        if not validate_justID(justID):
            data['error_message'] = 'That justID is not a valid JUST ID'
            data['response'] = 'Error'
            return Response(data)

        serializer = get_serializer(self._model,data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            serialize_user(data,user)
        else:
            data = serializer.errors
        return Response(data)

class RegisterSpecialNeedUser(RegisterUser):
    def __init__(self, **kwargs) -> None:
        super().__init__(model=SpecialNeed,**kwargs)


class RegisterVolunteerUser(RegisterUser):
    def __init__(self, **kwargs) -> None:
        super().__init__(model=Volunteer,**kwargs)

class RegisterAdminUser(RegisterUser):
    def __init__(self, **kwargs) -> None:
        super().__init__(model=Admin,**kwargs)

class login(APIView):

    authentication_classes = []
    permission_classes = []

    def post(self, request):
        context = {}
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(email=username, password=password)
        if user:
            serialize_user(context,user)
            context['response'] = 'successfully authenticated'
        else:
            context['response'] = 'Error'
            context['error_message'] = 'Invalid credentials'

        return Response(context)

class set_online(APIView):
    context = {}
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request):
        context = {}
        user = Token.objects.get(key=request.auth.key).user
        is_online = request.data.get('is_online')
        if user and is_online:
            
            user.is_online = True if (is_online == "true") else False
            user.save()
            serialize_user(context,user)
            context['response'] = 'successfully changed status'
            context["is_online"] = user.is_online
        elif not is_online:
            context['response'] = 'Error'
            context['error_message'] = 'You must provide a value'
        else:
            context['response'] = 'Error'
            context['error_message'] = 'Invalid credentials'

        return Response(context)