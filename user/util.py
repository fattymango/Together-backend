from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.authtoken.models import Token

from .token import account_activation_token


def email_exists(email):
	User = get_user_model()
	try:
		User.objects.get(email=email)
	except User.DoesNotExist:
		return False
	return True


def justID_exists(justID):
	User = get_user_model()
	try:
		User.objects.get(justID=justID)
	except User.DoesNotExist:
		return False
	return True


def serialize_user(data, user):
	data['response'] = 'successfully registered new user.'
	data['email'] = user.email
	data['justID'] = user.justID
	data['pk'] = user.pk
	token = Token.objects.get(user=user).key
	data['token'] = token


def send_verification_email(pk, name, email):
	mail_subject = 'Activation link has been sent to your email id'
	message = render_to_string('acc_active_email.html', {
		'name'  : name,
		'domain': "localhost",
		'uid'   : urlsafe_base64_encode(force_bytes(pk)),
		'token' : account_activation_token.make_token(get_user_model().objects.get(pk=pk)),
	})

	email = EmailMessage(
		mail_subject, message, to=[email]
	)
	return email.send()
