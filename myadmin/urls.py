from django.urls import path
from . import views

urlpatterns = [
        path('', views.Index.as_view(), name="admin-index"),
        path('login/', views.LoginView.as_view(), name="admin-login"),
        path('logout/', views.LogoutView.as_view(), name="admin-logout")
]

