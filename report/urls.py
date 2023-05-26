from django.urls import path
from . import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
	path("create/", views.CreateReport.as_view(), name="create_report"),

]

urlpatterns = format_suffix_patterns(urlpatterns)
