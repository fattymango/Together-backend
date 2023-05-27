from rest_framework import serializers

from chat.models import Message


class MessageSerializer(serializers.ModelSerializer):
	author = serializers.SlugRelatedField(
		many=False,
		read_only=True,
		slug_field='full_name'
	)

	class Meta:
		model = Message
		fields = ['id', 'author', 'message', 'date_created']
