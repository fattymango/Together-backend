import json
import logging

from django.db import models

from chat.models import ChatRoom
from user.models import Volunteer, SpecialNeed
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework import serializers

from user.serializers import BaseUserSerializer
from .tasks import task_send_request

logger = logging.getLogger(__name__)

HELP_TYPE = (('M', 'Movement'), ('V', 'Visual'), ('E', 'Else'))
GENDER_CHOICES = (('M', 'Male'), ('F', 'Female'), ("N", None))


# Create your models here.
class Request(models.Model):
	specialNeeds = models.ForeignKey(SpecialNeed, on_delete=models.CASCADE, null=False, blank=False)
	volunteer = models.ForeignKey(Volunteer, on_delete=models.CASCADE, null=True, blank=True)
	date_created = models.DateField(auto_now_add=True)
	location = models.CharField(max_length=50, null=False, blank=False)
	help_type = models.CharField(max_length=1, choices=HELP_TYPE, null=False, blank=False)
	square = models.CharField(max_length=2, blank=False, null=False, default="A")
	building = models.CharField(max_length=1, blank=True, null=True, )
	description = models.TextField(max_length=200, blank=False, null=False, default="no data")
	gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default="N")
	is_finished = models.BooleanField(default=False)

	def __str__(self) -> str:
		return str(self.pk) + " " + str(self.specialNeeds.justID) + " " + self.location


def clean_fields(request: Request, fields: list) -> dict:
	try:
		d = request.__dict__

		for field in fields:
			del d[field]
		return d
	except Exception as e:
		logger.error(e)
		raise e


class RequestSerializer(serializers.ModelSerializer):
	specialNeed = serializers.SerializerMethodField(method_name='get_specialNeeds')

	class Meta:
		model = Request
		fields = ['id', 'specialNeed', 'location', 'help_type', "gender", "square", "building", "description"]

	def get_specialNeeds(self, instance):
		return BaseUserSerializer(instance.specialNeeds).data


@receiver(post_save, sender=Request)
def create_chat_room(sender, instance: Request = None, created=False, **kwargs):
	if created:
		return ChatRoom.objects.create(specialNeeds=instance.specialNeeds, request=instance)


@receiver(post_save, sender=Request)
def send_request_to_volunteer(sender, instance: Request = None, created=False, **kwargs):
	if created:
		# serialized_request = clean_fields(instance, fields=["_state", "date_created", "is_finished"])
		serialized_request = dict(RequestSerializer(instance).data)
		return task_send_request.delay(serialized_request)

# {'id': 29,
# 'specialNeed': {'email': 'mhabdallah195@cit.just.edu.jo', 'justID': 6,
# 'token': 'b8c8bb4a14acebf1e1af69442cfe757269d2aa45', 'full_name': 'salem', 'gender': 'M',
# 'is_active': True, 'is_admin': False, 'is_online': True, # 'is_just_admin': False, 'is_volunteer': False, 'is_specialNeeds': True},
# 'location': 'A2', 'help_type': 'M', 'gender': 'M'}
