from django.db import models
from django.contrib.auth.models import (
	BaseUserManager, AbstractBaseUser
)
from django.db.models.signals import post_save
from rest_framework.authtoken.models import Token
import pandas
from user.signals import receiver_with_multiple_senders
from .tasks import send_verification_email_task

def validate_justID(justID):
	data = pandas.read_excel(r'user/static/justIDs.xlsx')
	IDs = pandas.DataFrame(data, columns=['justID'])
	return int(justID) in IDs.values


class MyUserManager(BaseUserManager):
	def create_user(self, email, justID, password):

		if not email:
			raise ValueError('Users must have an email address')
		if not justID:
			raise ValueError('Users must have an JUST ID')
		if not validate_justID(justID):
			raise ValueError('JUST ID is not valid')
		user = self.model(
			email=self.normalize_email(email),
			justID=justID
		)

		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_superuser(self, email, justID, password=None):
		"""
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
		user = self.create_user(
			email,
			justID=justID,
			password=password,

		)
		user.is_admin = True
		user.save(using=self._db)
		return user


class BaseUser(AbstractBaseUser):
	GENDER_CHOICES = (('M', 'Male'), ('F', 'Female'),)
	email = models.EmailField(verbose_name='email address', max_length=255, unique=True, )
	justID = models.PositiveIntegerField(verbose_name="university ID", unique=True, blank=False, null=False)
	full_name = models.CharField(verbose_name="full name", max_length=100)
	gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
	is_active = models.BooleanField(default=False)
	is_admin = models.BooleanField(default=False)
	is_online = models.BooleanField(default=False)

	objects = MyUserManager()

	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = ['justID']

	def __str__(self):
		return self.email + "," + str(self.justID)

	def has_perm(self, perm, obj=None):
		"Does the user have a specific permission?"
		# Simplest possible answer: Yes, always
		return self.is_admin

	def has_module_perms(self, app_label):
		"Does the user have permissions to view the app `app_label`?"
		# Simplest possible answer: Yes, always
		return True

	@property
	def is_staff(self):
		"Is the user a member of staff?"
		# Simplest possible answer: All admins are staff
		return self.is_admin


class SpecialNeed(BaseUser):
	DISABILITY_CHOICES = (('M', 'Movement'), ('V', 'Visual'), ('E', 'Else'))

	disability_type = models.CharField(verbose_name="type of disability", max_length=1, choices=DISABILITY_CHOICES)


class Volunteer(BaseUser):
	is_validated = models.BooleanField(verbose_name="is the user valid to volunteer", default=False)


class Admin(BaseUser):
	pass


@receiver_with_multiple_senders(post_save, senders=[BaseUser, Volunteer, SpecialNeed, Admin])
def create_auth_token(sender, instance=None, created=False, **kwargs):
	if created:
		Token.objects.create(user=instance)


@receiver_with_multiple_senders(post_save, senders=[BaseUser, Volunteer, SpecialNeed, Admin])
def send_verification_email(sender, instance=None, created=False, **kwargs):
	if created:
		return send_verification_email_task.delay(instance.pk,instance.justID,instance.email)

