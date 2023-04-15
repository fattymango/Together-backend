from django.urls import path
from . import views
from rest_framework.urlpatterns import format_suffix_patterns
urlpatterns = [
path("update/volunteer/<latitude>/<longitude>/",views.VolunteerUpdateLocation.as_view(),name="volunteer_update_location"),
path("update/specialneeds/<latitude>/<longitude>/",views.SpecialNeedsUpdateLocation.as_view(),name="specialneeds_update_location"),
]

urlpatterns = format_suffix_patterns(urlpatterns)