from asgiref.sync import async_to_sync
from django.db import models
from user.models import Volunteer, SpecialNeed
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer

# Create your models here.
class Request(models.Model):
	HELP_TYPE = (('M', 'Movement'), ('V', 'Visual'), ('E', 'Else'))
	specialNeeds = models.ForeignKey(SpecialNeed, on_delete=models.CASCADE, null=False, blank=False)
	volunteer = models.ForeignKey(Volunteer, on_delete=models.CASCADE, null=True, blank=True)
	date_created = models.DateField(auto_now_add=True)
	location = models.CharField(max_length=50, null=False, blank=False)
	help_type = models.CharField(max_length=1, choices=HELP_TYPE, null=False, blank=False)
	is_finished = models.BooleanField(default=False)
	def __str__(self) -> str:
		return str(self.pk) + " " + str(self.specialNeeds.justID) + " " + self.location


@receiver(post_save, sender=Request)
def create_auth_token(sender, instance : Request = None, created=False, **kwargs):
	if created:

		users = Volunteer.objects.filter(is_validated = True)
		channel_layer = get_channel_layer()
		for user in users:
			async_to_sync(channel_layer.group_send)("user"+str(user.pk), {"type": "chat_message", "data": {
				"specialNeeds": str(instance.specialNeeds.justID),
				"date_created": str(instance.date_created),
				"location":     str(instance.location),
				"help_type":    str(instance.help_type),
				"websocket":    "".join(["ws://localhost/ws/request/",str(instance.pk), "/"])
			}})