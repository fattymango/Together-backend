import pandas
from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.authtoken.models import Token


from .token import account_activation_token
import os

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


def serialize_user(user):
	return {
		'response': 'successfully registered new user.',
		'email'   : user.email,
		'justID'  : user.justID,
		'pk'      : user.pk,
		'token'   : Token.objects.get(user=user).key
	}


def send_verification_email(pk, name, email):
	mail_subject = 'Activation link'
	message = render_to_string('acc_active_email.html', {
		'name'  : name,
		'domain': os.environ.get("SITE_DOMAIN"),
		'uid'   : urlsafe_base64_encode(force_bytes(pk)),
		'token' : account_activation_token.make_token(get_user_model().objects.get(pk=pk)),
	})

	email = EmailMessage(
		mail_subject, message, to=[email]
	)
	return email.send()


def send_validation_volunteer_email(pk, name):
	mail_subject = 'Validation link'
	message = render_to_string('volunteer_validate_email.html', {
		'name'  : name,
		'domain': os.environ.get("SITE_DOMAIN"),
		'uid'   : urlsafe_base64_encode(force_bytes(pk)),
	})

	email = EmailMessage(
		mail_subject, message, to=[os.environ.get("VALIDATOR_EMAIL")]
	)
	return email.send()


def get_users_data():
	return pandas.read_excel(r'user/static/users.xlsx')


def get_specialneed_users():
	return pandas.read_excel(r'user/static/specialneeds.xlsx')


def fetch_user_data(justID):
	data = get_users_data()
	# Create a DataFrame object from list
	df = pandas.DataFrame(data,
	                      columns=['justID', 'name',
	                               'gender', 'type', "email"])

	df.set_index("justID", inplace=True)

	result = df.loc[justID]

	return result


def validate_justID(justID):
	data = get_users_data()
	IDs = pandas.DataFrame(data, columns=['justID'])
	return int(justID) in IDs.values


def validate_specialneed(justID):
	data = get_specialneed_users()
	IDs = pandas.DataFrame(data, columns=['justID'])
	return int(justID) in IDs.values
