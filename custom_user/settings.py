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

"""
Default settings. See __init__.py for code that injects these defaults
"""
from django.conf import settings

# This must be set to the python path (not including .models) of your primary subclass of User.
# Also, custom_user.models.User will always contain this class as a shortcut
CUSTOM_USER_MODEL = None

# This setting is used only if your user model inherits from CustomUser rather than EmailCustomUser. If you use CustomUser directly,
# and this settings is true, then the default forms will show email forms intead of login forms.
# TODO: Implement this
#CUSTOM_USER_EMAIL_LOGIN = False