# Copyright 2012 Concentric Sky, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from django.contrib.auth import backends, login
from django.core.exceptions import ImproperlyConfigured
from django.core.validators import email_re
from sky_visitor.utils import SubclassedUser as User


# Reference: http://groups.google.com/group/django-users/browse_thread/thread/39488db1864c595f
def auto_login(request, user):
    """
    Allows you to fake a login in your code
    """
    user.backend = 'sky_visitor.backends.BaseBackend'
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
