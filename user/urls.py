from django.urls import path
from . import views
from rest_framework.urlpatterns import format_suffix_patterns
urlpatterns = [
        path('api/volunteer/register', views.VolunteerUserRegistration.as_view(), name="volunteer-register"),
        path('api/specialneeds/register', views.SpecialNeedUserRegistration.as_view(), name="specialneeds-register"),
        path('api/admin/register', views.AdminUserRegistration.as_view(), name="admin-register"),
        path('api/login', views.UserLogin.as_view(), name="Login"),
        path('api/setonline', views.SetUserOnline.as_view(), name="SetUserOnline"),
        path('activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/',
             views.ActivateUser.as_view(), name='activate'),
        path('activate/(?P<uidb64>[0-9A-Za-z_\-]+)/',
             views.ValidateVolunteer.as_view(), name='validate'),
]

urlpatterns = format_suffix_patterns(urlpatterns)