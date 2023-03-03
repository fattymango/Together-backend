from rest_framework import serializers

from .models import Request


class RequestSerializer(serializers.ModelSerializer):
	class Meta:
		model = Request
		fields = ['id', 'specialNeeds', 'location', 'help_type', 'is_finished']


class UpdateRequestSerializer(RequestSerializer):
	class Meta(RequestSerializer.Meta):
		fields = RequestSerializer.Meta.fields + ['volunteer']
		extra_kwargs = {
			'id'          : {'read_only': True},
			'specialNeeds': {'read_only': True},
			'location'    : {'read_only': True},
			'help_type'   : {'read_only': True},
		}
