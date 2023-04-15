import logging

from django.contrib.auth import get_user_model, authenticate

from django import forms
logger = logging.getLogger(__name__)
class LoginForm (forms.ModelForm):
    password = forms.CharField(label="password",widget=forms.PasswordInput)

    class Meta :
        model = get_user_model()
        fields = ('email','password')

    def clean (self):
        if self.is_valid():
            logger.warning(self.cleaned_data)
            email = self.cleaned_data['email']
            password = self.cleaned_data['password']
            if not authenticate(username=email , password=password):
                raise forms.ValidationError('invalid password')