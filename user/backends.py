import logging

from django.contrib.auth import backends, get_user_model

logger = logging.getLogger(__name__)
UserModel = get_user_model()
class EmailOrJustIDModelBackend(backends.ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):

        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        if username is None or password is None:
            return None
        try:

            if username.isdigit():
                user = UserModel.objects.get(justID=username)
            else:
                user = UserModel.objects.get(email=username)

            if user.check_password(password) and self.user_can_authenticate(user):
                return user

        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            UserModel().set_password(password)
            return None
