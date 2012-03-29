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

from django.contrib.auth import models as auth_models
from django.contrib.auth import admin as auth_admin
from django.contrib import admin
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from extended_auth.forms import UserChangeAdminForm, UserCreateAdminForm
from extended_auth.utils import SubclassedUser as User


# Unregister the default User model to avoid confusion
admin.site.unregister(auth_models.User)

class EmailUserAdmin(auth_admin.UserAdmin):

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Groups'), {'fields': ('groups',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')}
        ),
    )
    list_display = ('email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('first_name', 'last_name', 'email')
    ordering = ('email',)

    form = UserChangeAdminForm
    add_form = UserCreateAdminForm
#    change_password_form = AdminPasswordChangeForm

admin.site.register(User, EmailUserAdmin)