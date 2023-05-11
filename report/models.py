from django.db import models
from django.conf import settings


# Create your models here.
class Report(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="report_user")
	request = models.ForeignKey("request.Request", on_delete=models.CASCADE, related_name="report_request")
	content = models.CharField(max_length=1000, null=False, blank=False)
	is_resolved = models.BooleanField(default=False)
	date_created = models.DateField(auto_now_add=True, blank=True, null=True)

	def __str__(self):
		return f'{self.user} - {self.request}'

	def save(self, *args, **kwargs):
		assigned_specialNeeds = self.request.specialNeeds.pk == self.user.pk
		assigned_volunteer = (self.request.volunteer != None and self.request.volunteer.pk == self.user.pk)

		if assigned_specialNeeds or assigned_volunteer:
			super(Report, self).save(*args, **kwargs)
		else:
			raise PermissionError(f"User {self.user} should be assigned to the request.")