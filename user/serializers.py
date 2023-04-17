from rest_framework import serializers

from .models import *
from .util import validate_justID, validate_specialneed


class UserRegistrationSerializer(serializers.ModelSerializer):
	password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

	class Meta:
		model = BaseUser
		fields = ['justID', 'password', 'password2']
		extra_kwargs = {
			'password': {'write_only': True},
		}

	def validate(self, attrs):

		justID = attrs['justID']
		if not validate_justID(justID):
			raise serializers.ValidationError({'justID': 'That justID is not valid.'})

		return attrs

	def save(self):
		justID = self.validated_data['justID']
		user = self.Meta.model.objects.create(justID=justID)
		password = self.validated_data['password']
		password2 = self.validated_data['password2']
		if password != password2:
			raise serializers.ValidationError({'password': 'Passwords must match.'})
		user.set_password(password)

		user.save()
		return user


fields = ['justID', 'password', 'password2']
extra_kwargs = {
	'password': {'write_only': True},
}


class SpecialNeedsRegistrationSerializer(UserRegistrationSerializer):
	class Meta:
		model = SpecialNeed
		fields = fields
		extra_kwargs = extra_kwargs

	def validate(self, attrs):
		justID = attrs['justID']
		if not validate_specialneed(justID):
			raise serializers.ValidationError({'justID': 'That justID is not a valid special needs student.'})

		return attrs

class VolunteerRegistrationSerializer(UserRegistrationSerializer):
	class Meta:
		model = Volunteer
		fields = fields
		extra_kwargs = extra_kwargs


class AdminRegistrationSerializer(UserRegistrationSerializer):
	class Meta:
		model = BaseUser
		fields = fields
		extra_kwargs = extra_kwargs

class UpdateVolunteerSerializer(serializers.ModelSerializer):
	class Meta:
		model = Volunteer
		fields = ['is_validated']
		
def get_serializer(model, data):
	if model == SpecialNeed:
		return SpecialNeedsRegistrationSerializer(data=data)
	elif model == Volunteer:
		return VolunteerRegistrationSerializer(data=data)
	elif model == BaseUser:
		return AdminRegistrationSerializer(data=data)
