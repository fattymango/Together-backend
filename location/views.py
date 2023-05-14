import logging
from time import sleep

from rest_framework import generics, views
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache
from django.conf import settings
from rest_framework.views import APIView

from .permissions import IsSpecialNeeds, IsVolunteer, CanGetVolunteersLocation

# Create your views here.
logger = logging.getLogger(__name__)


class UpdateLocation(generics.GenericAPIView):
    permission_classes = []
    authentication_classes = [TokenAuthentication]
    prefix = None

    def get_location(self, *args, **kwargs):
        return kwargs.get("latitude"), kwargs.get("longitude")

    def check_location(self, lat, long):
        if not lat:
            return status.HTTP_400_BAD_REQUEST, {"latitude": "You must provide a latitude."}

        if not long:
            return status.HTTP_400_BAD_REQUEST, {"longitude": "You must provide a longitude."}

        return True, ""

    def get(self, request, *args, **kwargs):

        lat, long = self.get_location(*args, **kwargs)
        user = request.user

        valid_status, message = self.check_location(lat,long)
        if not valid_status:
            return Response(data=message, status=valid_status)

        key = self.prefix.replace("*", (str(user.justID)))
        cache.set(key, (lat, long), timeout=2 * 60)
        return Response(data={"response": "Location updated successfully"})


class VolunteerUpdateLocation(UpdateLocation):
    permission_classes = [IsVolunteer]
    prefix = settings.CACHE_PREFIXES["LOCATION"]["VOLUNTEER"]

class SpecialNeedsUpdateLocation(UpdateLocation):
    permission_classes = [IsSpecialNeeds]
    prefix = settings.CACHE_PREFIXES["LOCATION"]["SPECIALNEEDS"]


class GetVolunteersCurrentLocation(APIView):
    permission_classes = [IsSpecialNeeds, CanGetVolunteersLocation]
    authentication_classes = [TokenAuthentication]

    def get(self, request, *args, **kwargs):
        try:
            key = settings.CACHE_PREFIXES["LOCATION"]["VOLUNTEER"].replace("*", (str(kwargs.get("pk"))))
            data = cache.get(key)

            return Response(data={"response": "success", "latitude": data[0], "longitude": data[1]})
        except:
            return Response(data={"response": "Error", "latitude": 0, "longitude": 0})
