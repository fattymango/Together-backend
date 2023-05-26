import logging

from django.shortcuts import render
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView

from report.models import Report
from request.permissions import IsSpecialNeeds, OwnsRequest
from .serializers import ReportSerializer
from .permissions import ReportExists, CanCreateReport
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

logger = logging.getLogger(__name__)


# Create your views here.
class CreateReport(generics.CreateAPIView):
	queryset = Report.objects.all()
	serializer_class = ReportSerializer
	permission_classes = [IsAuthenticated, IsSpecialNeeds, ReportExists, CanCreateReport]
	authentication_classes = [TokenAuthentication]

	def create(self, request, *args, **kwargs):
		try:

			try:
				request.data.update({'user': request.user.id})
			except AttributeError:
				request.data._mutable = True
				request.data.update({'user': request.user.id})

			return super().create(request, *args, **kwargs)
		except Exception:
			logging.critical(Exception, exc_info=True)
			return Response(data={"error": "error has occurred, please make sure the credentials are correct."},
			                status=status.HTTP_400_BAD_REQUEST)
