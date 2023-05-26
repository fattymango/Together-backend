import logging

from rest_framework import serializers

from user.models import SpecialNeed
from .models import Report

logger = logging.getLogger(__name__)


class ReportSerializer(serializers.ModelSerializer):
	class Meta:
		model = Report
		fields = ['id', 'user', 'request', 'rating', 'content', "is_resolved"]


class UpdateReportSerializer(serializers.ModelSerializer):
	class Meta:
		model = Report
		fields = ['is_resolved']
