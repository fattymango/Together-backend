import logging

from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views import View

from myadmin.forms import LoginForm
from report.models import Report
from user.models import Volunteer
from rest_framework.authtoken.models import Token
logger = logging.getLogger(__name__)


# Create your views here.
class Index(View):
	template_name = 'index.html'

	def get(self, request, *args, **kwargs):
		user = request.user
		message = ''
		context = {}
		if user.is_authenticated :
			if user.is_just_admin:
				context["message"] = ("hello" + str(user.justID))
				context["reports"] = Report.objects.all()
				context["volunteers"] = Volunteer.objects.filter()
				request.session['token'] = Token.objects.get(user = request.user).key
			else:
				context["message"] = ("You can't view this page, You are not a just staff. " + str(user.justID))
			return render(request,self.template_name,context)
		else:
			return redirect('admin-login')


class LoginView(View):
	template_name = 'login.html'
	form_class = LoginForm

	def get_context_data(self, **kwargs):
		context = super(LoginView, self).get_context_data(**kwargs)
		context["login_form"] = context["form"]
		return context

	def is_authenticated(self, request):
		return request.user.is_authenticated

	def get(self, request):
		if self.is_authenticated(request):
			return redirect('admin-index')

		form = self.form_class()
		message = ''

		return render(request, self.template_name, context={'login_form': form, 'message': message})

	def post(self, request):
		if self.is_authenticated(request):
			return redirect('admin-index')

		form = self.form_class(request.POST)

		if form.is_valid():

			user = authenticate(
				username=form.cleaned_data['email'],
				password=form.cleaned_data['password'],
			)

			if user is not None :
				if user.is_just_admin:
					login(request, user)
					return redirect('admin-index')


		message = "you must be a JUST staff to login."
		return render(request, self.template_name, context={'form': form,"message":message})


class LogoutView(View):

	def get(self, request):
		logout(request=request)
		return redirect('admin-login')
