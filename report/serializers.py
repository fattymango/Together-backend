from rest_framework import serializers

from .models import Report


class ReportSerializer(serializers.ModelSerializer):
	class Meta:
		model = Report
		fields = ['id', 'user', 'request', 'rating', 'content', "is_resolved"]


class UpdateReportSerializer(serializers.ModelSerializer):
	class Meta:
		model = Report
		fields = ['is_resolved']
