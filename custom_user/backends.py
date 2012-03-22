from django.contrib.auth import backends, login
from django.core.exceptions import ImproperlyConfigured
from django.core.validators import email_re
from custom_user.utils import SubclassedUser as User


# Reference: http://groups.google.com/group/django-users/browse_thread/thread/39488db1864c595f
def auto_login(request, user):
    # TODO TEST: this process
    user.backend = 'custom_user.backends.BaseBackend'
    login(request, user)


class BaseBackend(backends.ModelBackend):
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

class UsernameBackend(BaseBackend):
    def authenticate(self, username=None, password=None):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return None

        if user.check_password(password):
            return user
        else:
            return None

class EmailBackend(BaseBackend):
    def authenticate(self, email=None, password=None):
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return None

        if user.check_password(password):
            return user
        else:
            return None
