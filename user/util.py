from rest_framework.authtoken.models import Token
from .models import BasicUser



def email_exists(email):

	try:
		user = BasicUser.objects.get(email=email)
	except BasicUser.DoesNotExist:
		return False
	return True

def justID_exists(justID):
	try:
		user = BasicUser.objects.get(justID=justID)
	except BasicUser.DoesNotExist:
		return False
	return True


def serialize_user(data,user):
    data['response'] = 'successfully registered new user.'
    data['email'] = user.email
    data['justID'] = user.justID
    data['pk'] = user.pk
    token = Token.objects.get(user=user).key
    data['token'] = token
	