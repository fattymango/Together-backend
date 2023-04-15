import json
import logging

from django.db import models

from chat.models import ChatRoom
from user.models import Volunteer, SpecialNeed
from django.db.models.signals import post_save
from django.dispatch import receiver

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
	gender = models.CharField(max_length=1, choices=GENDER_CHOICES ,default="N")
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

@receiver(post_save, sender=Request)
def create_chat_room(sender, instance: Request = None, created=False, **kwargs):
	if created:
		return ChatRoom.objects.create(specialNeeds=instance.specialNeeds,request=instance)

@receiver(post_save, sender=Request)
def send_request_to_volunteer(sender, instance: Request = None, created=False, **kwargs):
	if created:
		# update_location
		serialized_request = clean_fields(instance, fields=["_state", "date_created", "is_finished"])
		return task_send_request.delay(serialized_request)
