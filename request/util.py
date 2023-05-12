import logging
from time import sleep

from asgiref.sync import async_to_sync

from django.core.cache import cache
from django.conf import settings
from geopy.distance import geodesic
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
import os
from random import shuffle

MAX_DISTANCE_METERS = 500
channel_layer = get_channel_layer()
logger = logging.getLogger(__name__)


def calculate_distance(request_location, volunteer_location) -> float:
	return geodesic(tuple(request_location.split(",")), volunteer_location).meters


def distance_match(distance, volunteers_available) -> bool:
	if distance < 300:
		return True

	elif volunteers_available < 20:
		if distance < MAX_DISTANCE_METERS:
			return True

	return False


def get_volunteer_is_available(volunteer: get_user_model()):
	is_availabe = cache.get(settings.CACHE_PREFIXES["VOLUNTEER"]["STATUS"].replace("*", str(volunteer.justID)))
	return is_availabe and volunteer.is_online


def set_volunteer_is_available(justID, value: bool):
	cache.set(settings.CACHE_PREFIXES["VOLUNTEER"]["STATUS"].replace("*", str(justID)), value)


def gender_match(specialneeds_gender, volunteer_gender) -> bool:
	if specialneeds_gender == 'N':
		return True
	return specialneeds_gender == volunteer_gender


def cache_request_status(request_pk, status) -> None:
	cache.set(settings.CACHE_PREFIXES["REQUEST"]["STATUS"].replace("*", str(request_pk)), status)


def get_request_status(request_pk) -> bool:
	return cache.get(settings.CACHE_PREFIXES["REQUEST"]["STATUS"].replace("*", str(request_pk)))


def get_volunteers_locations() -> list:
	return cache.keys(settings.CACHE_PREFIXES["LOCATION"]["VOLUNTEER"])


def generate_websocket(*args, **kwargs) -> str:
	url_args = ["ws://", os.environ["SITE_DOMAIN"], "/"]
	try:
		for key, value in kwargs.items():
			url_args += value + "/"
	except Exception as e:
		logger.error(e)
	return "".join(url_args)


def send_request_consumer_message(request_pk, data) -> None:
	return async_to_sync(channel_layer.group_send)("request%s" % str(request_pk),
	                                               {"type": "chat_message", "data": data})


def send_request(user, request) -> None:
	request["request_websocket"] = generate_websocket(prefix="ws", view_name="request", volunteer="volunteer",
	                                                  request_id=str(request["id"]))
	request["chatroom_websocket"] = generate_websocket(prefix="ws", view_name="chatroom", request_id=str(request["id"]))

	async_to_sync(channel_layer.group_send)("user" + str(user.justID), {"type": "chat_message", "data": request})


def send_request_to_volunteer(request):
	User = get_user_model()
	volunteers = get_volunteers_locations()
	shuffle(volunteers)

	for key in volunteers:

		volunteer_location = cache.get(key)
		volunteer = User.objects.get(justID=int(key.split("volunteer_", 1)[1]))

		if gender_match(request["gender"], volunteer.gender):

			distance = calculate_distance(request["location"], volunteer_location)

			if distance_match(distance, len(volunteers)) and get_volunteer_is_available(volunteer):
				send_request(volunteer, request)
				set_volunteer_is_available(volunteer.justID, False)
				cache_request_status(str(request["id"]), False)
				return True

	sleep(10)
	send_request_consumer_message(request["id"], {"response": "Error",
	                                              "message" : "We couldn't find a volunteer for you, please try again."})
	return False
