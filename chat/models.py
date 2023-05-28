from django.db import models
from django.conf import settings


# Create your models here.
class ChatRoom(models.Model):
	specialNeeds = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_room_specialNeeds')
	volunteer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='chat_room_volunteer')
	request = models.ForeignKey('request.Request', on_delete=models.CASCADE, related_name='chat_room_request')
	date_created = models.DateField(auto_now_add=True, blank=True, null=True)

	def __str__(self):
		return f'{self.specialNeeds} - {self.volunteer}'


class Message(models.Model):
	author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='message_author')
	room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, null=True)
	message = models.CharField(max_length=100, blank=True, null=True)
	date_created = models.DateTimeField(auto_now_add=True, blank=True, null=True)

	def __str__(self):
		return f'{self.author.full_name} - {self.message}'
