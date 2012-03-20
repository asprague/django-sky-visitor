from django import forms
from django.conf import settings
from django.contrib.auth import forms as auth_forms, authenticate
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User as AuthUser
from custom_user.utils import SubclassedUser as User
from custom_user.fields import UniqueRequiredEmailField, PasswordRulesField


# All user forms should inherit from this form to make sure email is unique
class BaseUserCreateForm(forms.ModelForm):
    email = UniqueRequiredEmailField()

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email',]

    def __init__(self, *args, **kwargs):
        super(BaseUserCreateForm, self).__init__(*args, **kwargs)

        if 'first_name' in self.fields and 'last_name' in self.fields:
            self.fields['first_name'].required = True
            self.fields['last_name'].required = True

class UserCreateAdminForm(forms.ModelForm):
    password1 = PasswordRulesField(label=_("Password"))
    username = None
    # TODO: Need a way to have a username-based option and an email-based option

    def __init__(self, *args, **kwargs):
        super(UserCreateAdminForm, self).__init__(*args, **kwargs)

    email = UniqueRequiredEmailField()
    password1 = PasswordRulesField(label=_("Password"))
    password2 = forms.CharField(label=_("Password confirmation"), widget=forms.PasswordInput,
        help_text = _("Enter the same password as above, for verification."))

    class Meta:
        model = User
        fields = ("email",)
        exclude = ('username',)

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1", "")
        password2 = self.cleaned_data["password2"]
        if password1 != password2:
            raise forms.ValidationError(_("The two password fields didn't match."))
        return password2

    def save(self, commit=True):
        user = super(UserCreateAdminForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeAdminForm(auth_forms.UserChangeForm):
    email = UniqueRequiredEmailField()
    # TODO: Need a way to have a username-based option and an email-based option


# TODO: Inheriting from this form creates a auth.User instead of a subclassed User. Fix that.
class RegisterForm(auth_forms.UserCreationForm):
    email = UniqueRequiredEmailField()

    class Meta:
        model = User
        fields = ['username', 'email',]


class InvitationForm(BaseUserCreateForm):
    email = UniqueRequiredEmailField()

    def save(self, commit=True):
        user = super(InvitationForm, self).save(commit=False)
        # Make them unactivated
        user.is_active = False
        if commit:
            user.save()
        return user


class SetPasswordForm(auth_forms.SetPasswordForm):
    new_password1 = PasswordRulesField(label=_("New password"))


# Borrowed from core so we can define our own inheritance
class PasswordChangeForm(SetPasswordForm):
    """
    A form that lets a user change his/her password by entering
    their old password.
    """
    old_password = forms.CharField(label=_("Old password"), widget=forms.PasswordInput)

    def clean_old_password(self):
        """
        Validates that the old_password field is correct.
        """
        old_password = self.cleaned_data["old_password"]
        if not self.user.check_password(old_password):
            raise forms.ValidationError(_("Your old password was entered incorrectly. Please enter it again."))
        return old_password
PasswordChangeForm.base_fields.keyOrder = ['old_password', 'new_password1', 'new_password2']


class InvitationCompleteForm(forms.ModelForm):
    email = UniqueRequiredEmailField()
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class EmailLoginForm(forms.Form):
    # NOTE: We choose not to extend AuthenticationForm here because we don't need the username field
    email = forms.CharField(label=_("Email"), max_length=75)
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        self.user_cache = None
        super(EmailLoginForm, self).__init__(*args, **kwargs)

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email and password:
            self.user_cache = authenticate(email=email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(_("Please enter a correct username and password. Note that both fields are case-sensitive."))
            elif not self.user_cache.is_active:
                raise forms.ValidationError(_("This account is inactive."))
        return self.cleaned_data

    def get_user_id(self):
        if self.user_cache:
            return self.user_cache.id
        return None

    def get_user(self):
        return self.user_cache

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']