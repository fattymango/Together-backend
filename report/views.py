import logging

from django.shortcuts import render

from report.models import Report
from .serializers import ReportSerializer,UpdateReportSerializer
from .permissions import CanCreateReport,IsAdmin,ReportExists
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework import generics
logger = logging.getLogger(__name__)
# Create your views here.
class CreateReport(generics.CreateAPIView):
	queryset = Report.objects.all()
	serializer_class = ReportSerializer
	permission_classes = [IsAuthenticated, ReportExists,CanCreateReport]
	authentication_classes = [TokenAuthentication]

class UpdateReport(generics.UpdateAPIView):
	queryset = Report.objects.all()
	serializer_class = UpdateReportSerializer
	permission_classes = [IsAuthenticated, IsAdmin]
	authentication_classes = [TokenAuthentication]
