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

	def set_model(self, justID):
		if validate_specialneed(justID):
			self.Meta.model = SpecialNeed
		else:
			self.Meta.model = Volunteer

	def save(self):
		justID = self.validated_data['justID']
		self.set_model(justID)
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


class UpdateVolunteerSerializer(serializers.ModelSerializer):
	class Meta:
		model = Volunteer
		fields = ['is_validated']


class BaseUserSerializer(serializers.ModelSerializer):
	is_volunteer = serializers.SerializerMethodField(method_name='get_is_volunteer')
	is_specialNeeds = serializers.SerializerMethodField(method_name='get_is_specialNeeds')
	is_validated = serializers.SerializerMethodField(method_name='get_is_validated')
	token = serializers.SerializerMethodField(method_name='get_token')

	class Meta:
		model = BaseUser
		fields = ['id', 'email', 'justID', 'token', 'full_name', 'gender', 'is_active', "is_validated", 'is_admin',
		          'is_online', 'is_just_admin', 'is_volunteer', 'is_specialNeeds', "phone_number"]

	def get_is_volunteer(self, instance):
		User = Volunteer
		try:
			User.objects.get(justID=instance.justID)
			return True
		except User.DoesNotExist:
			return False

	def get_is_validated(self, instance):
		User = Volunteer
		try:
			return User.objects.get(justID=instance.justID).is_validated
		except Exception:
			return False

	def get_is_specialNeeds(self, instance):
		User = SpecialNeed
		try:
			User.objects.get(justID=instance.justID)
			return True
		except User.DoesNotExist:
			return False

	def get_token(self, instance):
		return Token.objects.get(user=instance).key


class CanVolunteerSerializer(serializers.ModelSerializer):
	class Meta:
		model = Volunteer
		fields = ['is_validated']
# def get_serializer(model, data):
# 	if model == SpecialNeed:
# 		return SpecialNeedsRegistrationSerializer(data=data)
# 	elif model == Volunteer:
# 		return VolunteerRegistrationSerializer(data=data)
# 	elif model == BaseUser:
# 		return AdminRegistrationSerializer(data=data)
