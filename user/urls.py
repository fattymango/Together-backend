from django.urls import path
from . import views
from rest_framework.urlpatterns import format_suffix_patterns
urlpatterns = [
	path('api/register/', views.UserRegistration.as_view(), name="volunteer-register"),

	path('api/login/', views.UserLogin.as_view(), name="Login"),
	path('api/volunteer/setonline/', views.SetVolunteerOnline.as_view(), name="SetVolunteerOnline"),
	path('api/specialneeds/setonline/', views.SetSpecialNeedsOnline.as_view(), name="SetSpecialNeedsOnline"),
	path('activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/',
	     views.ActivateUser.as_view(), name='activate'),
	path('activate/<int:justID>/',
	     views.ValidateVolunteer.as_view(), name='validate_user'),
	path("api/", views.GetUserInfo.as_view())
]

urlpatterns = format_suffix_patterns(urlpatterns)