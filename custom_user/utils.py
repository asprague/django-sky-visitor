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

def get_user_model():
    from django.conf import settings
    # Grab the user model path
    custom_user_model_path = getattr(settings, 'CUSTOM_USER_MODEL', None)
    if custom_user_model_path is None:
        raise Exception(u"Cannot find your specified CUSTOM_USER_MODEL. Is CUSTOM_USER_MODEL in your settings.py? Are CustomUser and your CustomUser-subclass app both in your INSTALLED_APPS?")

    parts = custom_user_model_path.split('.')
    model_name = parts.pop()
    parts.append('models')
    module = __import__('.'.join(parts))
    return getattr(module.models, model_name)


#class SubclassedUserHolder(object):
#
#    override_user_model = None
#
#    @classmethod
#    def get_user_model(cls):
#        if cls.override_user_model:
#            return cls.override_user_model
#        else:
#            return get_user_model()


SubclassedUser = get_user_model()


def is_email_only():
    return SubclassedUser._is_email_only

