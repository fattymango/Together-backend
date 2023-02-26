from rest_framework import serializers

from .models import *


class UserRegistrationSerializer(serializers.ModelSerializer):


    password2 				= serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = BasicUser
        fields = ['email', 'justID', 'password', 'password2']
        extra_kwargs = {
                'password': {'write_only': True},
        }	

    def	save(self):
        
        
        user = self.Meta.model(email=self.validated_data['email'],justID=self.validated_data['justID'])
        password = self.validated_data['password']
        password2 = self.validated_data['password2']
        if password != password2:
            raise serializers.ValidationError({'password': 'Passwords must match.'})
        user.set_password(password)
        user.save()
        return user

fields = ['email', 'justID', 'password', 'password2']
extra_kwargs = {
                'password': {'write_only': True},
        }	   
class SpecialNeedsRegistrationSerializer(UserRegistrationSerializer):
    class Meta:
        model = SpecialNeed
        fields = fields
        extra_kwargs =  extra_kwargs

class VolunteerRegistrationSerializer(UserRegistrationSerializer):
   class Meta:
        model = Volunteer
        fields = fields
        extra_kwargs =  extra_kwargs
class AdminRegistrationSerializer(UserRegistrationSerializer):
   class Meta:
        model = Admin
        fields = fields
        extra_kwargs =  extra_kwargs

def get_serializer(model,data):
    if model == SpecialNeed:
        return SpecialNeedsRegistrationSerializer(data=data)
    elif model == Volunteer:
        return VolunteerRegistrationSerializer(data=data)
    elif model == Admin:
        return AdminRegistrationSerializer(data=data) 






