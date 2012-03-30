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

from django.utils.translation import ugettext_lazy as _
from django.utils.unittest.case import skipUnless
from extended_auth.settings import get_app_setting



def get_user_model():
    from django.conf import settings
    # Grab the user model path
    extened_user_model_path = get_app_setting('EXTENDED_AUTH_USER_MODEL')
    if extened_user_model_path is None:
        raise Exception(_("Cannot find your specified EXTENDED_AUTH_USER_MODEL. Is EXTENDED_AUTH_USER_MODEL in your settings.py? Are ExtendedUser and your ExtendedUser-subclass app both in your INSTALLED_APPS?"))

    parts = extened_user_model_path.split('.')
    model_name = parts.pop()
    parts.append('models')
    # Empty fromlist causes it to import "baz" when given "foo.bar.baz" ... Without it, it imports "foo"
    module = __import__('.'.join(parts), fromlist=[''])
    return getattr(module, model_name)

SubclassedUser = get_user_model()


def is_subclassed_user():
    return hasattr(SubclassedUser, '_is_email_only')

def is_username_user():
    return hasattr(SubclassedUser, '_is_email_only') and not SubclassedUser._is_email_only

def is_email_only():
    return hasattr(SubclassedUser, '_is_email_only') and SubclassedUser._is_email_only

def is_auth_user():
    from django.contrib.auth.models import User as AuthUser
    return isinstance(SubclassedUser, AuthUser)
