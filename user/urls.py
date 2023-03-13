from django.urls import path
from . import views
from rest_framework.urlpatterns import format_suffix_patterns
urlpatterns = [
path('api/volunteer/register', views.RegisterVolunteerUser.as_view(), name="volunteer-register"),
path('api/specialneeds/register', views.RegisterSpecialNeedUser.as_view(), name="specialneeds-register"),
path('api/admin/register', views.RegisterAdminUser.as_view(), name="admin-register"),
path('api/Login', views.Login.as_view(), name="Login"),
path('api/setonline', views.SetOnline.as_view(), name="SetOnline"),
]

urlpatterns = format_suffix_patterns(urlpatterns)