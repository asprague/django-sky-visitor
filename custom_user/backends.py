from django.contrib.auth import backends, login
from django.core.exceptions import ImproperlyConfigured
from django.core.validators import email_re
from custom_user.utils import SubclassedUser as User


# Reference: http://groups.google.com/group/django-users/browse_thread/thread/39488db1864c595f
def auto_login(request, user):
    # TODO TEST: this process
    user.backend = 'custom_user.backends.BaseBackend'
    login(request, user)

# Reference: http://nigel.jp/2011/06/django-user-authentication-and-extending-the-user-model/
class BaseBackend(backends.ModelBackend):
    def get_user(self, user_id):
        try:
            return self.user_class.objects.get(pk=user_id)
        except self.user_class.DoesNotExist:
            return None

    @property
    def user_class(self):
        if not hasattr(self, '_user_class'):
            self._user_class = User
            if not self._user_class:
                raise ImproperlyConfigured('Could not get custom user model')
        return self._user_class

class UsernameBackend(BaseBackend):
    def authenticate(self, username=None, password=None):
        try:
            user = self.user_class.objects.get(username=username)
        except self.user_class.DoesNotExist:
            return None

        if user.check_password(password):
            return user
        else:
            return None

class EmailBackend(BaseBackend):
    def authenticate(self, email=None, password=None):
        try:
            user = self.user_class.objects.get(email=email)
        except self.user_class.DoesNotExist:
            return None

        if user.check_password(password):
            return user
        else:
            return None
