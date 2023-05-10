from django.db import models
from django.contrib.auth.models import (
	BaseUserManager, AbstractBaseUser
)
from django.db.models.signals import post_save
from rest_framework.authtoken.models import Token
from user.signals import receiver_with_multiple_senders
from .tasks import task_send_verification_email, task_send_volunteer_validation_email
from .util import validate_justID, fetch_user_data

from django.dispatch import receiver


class MyBaseUserManager(BaseUserManager):
	def create(self, **obj_data):
		# Do some extra stuff here on the submitted data before saving...
		# For example...
		data = fetch_user_data(obj_data["justID"])
		obj_data["email"] = data["email"]
		obj_data["gender"] = data["gender"]
		obj_data["full_name"] = data["name"]
		# Now call the super method which does the actual creation
		return super().create(**obj_data)  # Python 3 syntax!!

	def create_user(self, justID, password):

		if not justID:
			raise ValueError('Users must have an JUST ID')
		if not validate_justID(justID):
			raise ValueError('JUST ID is not valid')
		user = self.model.objects.create(
			justID=justID
		)

		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_superuser(self, justID, password=None):

		user = self.create_user(
			justID=justID,
			password=password,

		)
		user.is_admin = True
		user.save(using=self._db)
		return user


class SpecialNeedManager(BaseUserManager):
	def create(self, **obj_data):
		# Do some extra stuff here on the submitted data before saving...
		# For example...
		data = fetch_user_data(obj_data["justID"])
		obj_data["email"] = data["email"]
		obj_data["gender"] = data["gender"]
		obj_data["full_name"] = data["name"]
		obj_data["disability_type"] = data["type"]

		# Now call the super method which does the actual creation
		return super().create(**obj_data)  # Python 3 syntax!!


GENDER_CHOICES = (('M', 'Male'), ('F', 'Female'),)


class BaseUser(AbstractBaseUser):
	email = models.EmailField(verbose_name='email address', max_length=255, unique=True, )
	justID = models.PositiveIntegerField(verbose_name="university ID", unique=True, blank=False, null=False)
	full_name = models.CharField(verbose_name="full name", max_length=100)
	gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
	is_active = models.BooleanField(default=False)
	is_admin = models.BooleanField(default=False)
	is_online = models.BooleanField(default=False)
	is_just_admin = models.BooleanField(default=False)
	objects = MyBaseUserManager()

	USERNAME_FIELD = 'justID'
	REQUIRED_FIELDS = []

	def __str__(self):
		return self.email + "," + str(self.justID)

	def has_perm(self, perm, obj=None):
		return self.is_admin

	def has_module_perms(self, app_label):
		return True

	@property
	def is_staff(self):
		return self.is_admin


class SpecialNeed(BaseUser):
	DISABILITY_CHOICES = (('M', 'Movement'), ('V', 'Visual'), ('E', 'Else'))

	disability_type = models.CharField(verbose_name="type of disability", max_length=1, choices=DISABILITY_CHOICES)
	objects = SpecialNeedManager()


class Volunteer(BaseUser):
	is_validated = models.BooleanField(verbose_name="is the user valid to volunteer", default=False)


@receiver_with_multiple_senders(post_save, senders=[BaseUser, Volunteer, SpecialNeed])
def create_auth_token(sender, instance=None, created=False, **kwargs):
	if created:
		Token.objects.create(user=instance)


@receiver(post_save, sender=Volunteer)
def send_validation_email(sender, instance=None, created=False, **kwargs):
	if created:
		return task_send_volunteer_validation_email.delay(instance.pk, instance.full_name)


@receiver_with_multiple_senders(post_save, senders=[BaseUser, Volunteer, SpecialNeed])
def send_verification_email(sender, instance=None, created=False, **kwargs):
	if created:
		return task_send_verification_email.delay(instance.pk, instance.full_name, instance.email)
