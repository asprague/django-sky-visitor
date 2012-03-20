from django.contrib.auth import models as auth_models
from django.contrib.auth import admin as auth_admin
from django.contrib import admin
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from custom_user.forms import UserChangeAdminForm, UserCreateAdminForm
from custom_user.utils import SubclassedUser as User


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