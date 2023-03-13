from django.urls import path
from . import views
from rest_framework.urlpatterns import format_suffix_patterns
urlpatterns = [
path('api/volunteer/register', views.RegisterVolunteerUser.as_view(), name="volunteer-register"),
path('api/specialneeds/register', views.RegisterSpecialNeedUser.as_view(), name="specialneeds-register"),
path('api/admin/register', views.RegisterAdminUser.as_view(), name="admin-register"),
path('api/login', views.login.as_view(), name="login"),
path('api/setonline', views.set_online.as_view(), name="set_online"),
]

urlpatterns = format_suffix_patterns(urlpatterns)