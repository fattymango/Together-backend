from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.conf import settings

from user.models import SpecialNeed


# Create your models here.
class Report(models.Model):
	user = models.ForeignKey(SpecialNeed, on_delete=models.CASCADE, related_name="report_user")
	request = models.ForeignKey("request.Request", on_delete=models.CASCADE, related_name="report_request", null=True,
	                            blank=True)
	content = models.CharField(max_length=1000, null=True, blank=True)
	rating = models.IntegerField(
		blank=False,
		null=False,
		default=5,
		validators=[MaxValueValidator(5), MinValueValidator(0)]
	)
	is_resolved = models.BooleanField(default=False)
	date_created = models.DateField(auto_now_add=True, blank=True, null=True)

	def __str__(self):
		return f'{self.user} - {self.request}'

# def save(self, *args, **kwargs):
# 	assigned_specialNeeds = self.request.specialNeeds.pk == self.user.pk
# 	assigned_volunteer = (self.request.volunteer != None and self.request.volunteer.pk == self.user.pk)
#
# 	if assigned_specialNeeds or assigned_volunteer:
# 		super(Report, self).save(*args, **kwargs)
# 	else:
# 		raise PermissionError(f"User {self.user} should be assigned to the request.")
