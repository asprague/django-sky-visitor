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

import urlparse
from sky_visitor.emails import TokenTemplateEmail
from django.contrib import messages
from django.contrib.auth import REDIRECT_FIELD_NAME, login, logout
from django.contrib.auth.tokens import default_token_generator
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.utils.http import base36_to_int
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.generic.base import RedirectView
from django.views.generic.edit import FormView, UpdateView, CreateView
from django.utils.translation import ugettext_lazy as _
from sky_visitor.backends import auto_login
from sky_visitor.forms import *
from sky_visitor.utils import SubclassedUser as User, is_email_only
from django.contrib.auth.models import User as AuthUser
from django.conf import settings


class RegisterView(CreateView):
    model = User
    template_name = 'sky_visitor/register.html'
    success_message = _("Successfully registered and signed in")
    login_on_success = True
    # TODO: Finish implementing this view

    def get_form_class(self):
        if is_email_only():
            return EmailRegisterForm
        else:
            return RegisterForm

    def form_valid(self, form):
        response = super(RegisterView, self).form_valid(form)
        user = self.object
        auto_login(self.request, user)
        messages.success(self.request, self.success_message)
        return response

    def get_success_url(self):
        return settings.LOGIN_REDIRECT_URL


# Originally from: https://github.com/stefanfoulis/django-class-based-auth-views/blob/develop/class_based_auth_views/views.py
class LoginView(FormView):
    """
    This is a class based version of django.contrib.auth.views.login.

    Usage:
        in urls.py:
            url(r'^login/$',
                LoginView.as_view(
                    form_class=MyVisitorFormClass,
                    success_url='/my/custom/success/url/),
                name="login"),

    """
    redirect_field_name = REDIRECT_FIELD_NAME
    success_url_overrides_redirect_field = False
    template_name = 'sky_visitor/login.html'

    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super(LoginView, self).dispatch(*args, **kwargs)

    def get_form_class(self):
        # TODO: Support email+username login when in username-mode
        if is_email_only():
            return EmailLoginForm
        else:
            return LoginForm

    def form_valid(self, form):
        """
        The user has provided valid credentials (this was checked in AuthenticationForm.is_valid()). So now we
        can log him in.
        """
        login(self.request, form.get_user())
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        """
        This will default to the "next" field if available, unless success_url_overrides_redirect_field is True, then it will default to that.
        """
        redirect_to = self.request.REQUEST.get(self.redirect_field_name, '')

        if self.success_url and (self.success_url_overrides_redirect_field or not redirect_to):
            redirect_to = self.success_url

        netloc = urlparse.urlparse(redirect_to)[1]
        if not redirect_to:
            redirect_to = settings.LOGIN_REDIRECT_URL
        elif netloc and netloc != self.request.get_host():
            redirect_to = settings.LOGIN_REDIRECT_URL
        return redirect_to

    def set_test_cookie(self):
        self.request.session.set_test_cookie()

    def check_and_delete_test_cookie(self):
        if self.request.session.test_cookie_worked():
            self.request.session.delete_test_cookie()
            return True
        return False

    def get(self, request, *args, **kwargs):
        """
        Same as django.views.generic.edit.ProcessFormView.get(), but adds test cookie stuff
        """
        self.set_test_cookie()
        return super(LoginView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Same as django.views.generic.edit.ProcessFormView.post(), but adds test cookie stuff
        """
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            self.check_and_delete_test_cookie()
            return self.form_valid(form)
        else:
            self.set_test_cookie()
            return self.form_invalid(form)


class SendTokenEmailMixin(object):
    email_template_class = TokenTemplateEmail

    def get_email_kwargs(self, user):
        return {'user': user}

    def send_email(self, user):
        """
        """
        email_template = self.email_template_class(**self.get_email_kwargs(user))
        return email_template.send_email()


class InvitationMixin(SendTokenEmailMixin):
    form_class = InvitationForm

    def form_valid(self, form):
        redirect = super(InvitationMixin, self).form_valid(form)
        self.send_email(self.get_user_object())
        return redirect

    def get_user_object(self):
        """
        Allows you to override to specify a custom way to grab the user that will be emailed

        Useful for more dynamic ways of adding a user (like when you have two forms on the same page.

        Defaults to self.object assuming that the primary form on the view is a user form.
        """
        return self.object


class InvitationView(InvitationMixin, FormView):
    # TODO: Change this to be a CreateView and define good defaults here.
    template_name = 'sky_visitor/invite.html'
    # Need to define success_url or override get_success_url()
    pass


class TokenValidateMixin(object):
    token_generator = default_token_generator
    display_message_on_invalid_token = True
    is_token_valid = False
    invalid_token_message = "This one-time use URL has already been used. Try to login or use the forgot password form."

    def get_token_generator(self):
        return self.token_generator

    def dispatch(self, request, *args, **kwargs):
        uidb36 = kwargs['uidb36']
        token = kwargs['token']
        assert uidb36 is not None and token is not None  # checked by URLconf
        try:
            uid_int = base36_to_int(uidb36)
            # Get an AuthUser instance here since we don't need any of the extra aspects of the SubclassedUser
            self._user = AuthUser.objects.get(id=uid_int)
        except (ValueError, AuthUser.DoesNotExist):
            self._user = None
        self.is_token_valid = (self._user is not None and self.get_token_generator().check_token(self._user, token))
        if not self.is_token_valid:
            return self.token_invalid(request, *args, **kwargs)
        return super(TokenValidateMixin, self).dispatch(request, *args, **kwargs)

    def token_invalid(self, request, *args, **kwargs):
        if self.display_message_on_invalid_token:
            messages.error(request, self.invalid_token_message, fail_silently=True)
        return HttpResponseRedirect(reverse('login'))

    def get_user_from_token(self):
        return self._user


class InvitationCompleteView(TokenValidateMixin, UpdateView):
    form_class = InvitationCompleteForm
    form_class_set_password = SetPasswordForm
    context_object_name = 'invited_user'
    auto_login_on_success = True
    template_name = 'sky_visitor/invite_complete.html'
    invalid_token_message = _("This one-time use invite URL has already been used. This means you have likely already created an account. Please try to login or use the forgot password form.")
    # Since this is an UpdateView, the defautl success_url will be the user's get_absolute_url(). Override if you'd like different behavior

    def get_object(self, queryset=None):
        return self.get_user_from_token()

    def post(self, request, *args, **kwargs):
        if self.is_token_valid:
            return super(InvitationCompleteView, self).post(request, *args, **kwargs)
        else:
            return self.get(request, *args, **kwargs)

    def form_valid(self, form):
        context = self.get_context_data()
        set_password_form = context['set_password_form']

        if set_password_form.is_valid():
            set_password_form.save(commit=True)
        else:
            return self._form_invalid(form, set_password_form)

        form.instance.is_active = True
        if self.auto_login_on_success:
            auto_login(self.request, form.instance)
        return super(InvitationCompleteView, self).form_valid(form)  # Save and redirect

    def form_invalid(self, form):
        return self._form_invalid(form)

    def _form_invalid(self, form, set_password_form=None):
        return self.render_to_response(self.get_context_data(form=form, set_password_form=set_password_form))

    def get_form(self, form_class):
        if self.is_token_valid:
            return super(InvitationCompleteView, self).get_form(form_class)
        else:
            return None

    def get_context_data(self, **kwargs):
        context_data = super(InvitationCompleteView, self).get_context_data(**kwargs)
        # TODO: Find a better way to mixin two forms in this view
        if self.is_token_valid:
            if 'set_password_form' not in context_data or context_data['set_password_form'] is None:
                if self.request.POST:
                    context_data['set_password_form'] = self.form_class_set_password(self.get_user_from_token(), self.request.POST, prefix='set_password')
                else:
                    context_data['set_password_form'] = self.form_class_set_password(self.get_user_from_token(), prefix='set_password')
        else:
            context_data['set_password_form'] = None
        return context_data


class LogoutView(RedirectView):
    success_message = "Successfully logged out."

    def get(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, self.success_message, fail_silently=True)
        return super(LogoutView, self).get(request, *args, **kwargs)

    def get_redirect_url(self, **kwargs):
        return reverse('login')


class ForgotPasswordView(SendTokenEmailMixin, FormView):
    form_class = PasswordResetForm
    template_name = 'sky_visitor/forgot_password_start.html'

    def form_valid(self, form):
        user = form.users_cache[0]
        self.send_email(user)
        return super(ForgotPasswordView, self).form_valid(form)  # Do redirect

    def get_email_kwargs(self, user):
        kwargs = super(ForgotPasswordView, self).get_email_kwargs(user)
        domain = self.request.get_host()
        kwargs['email_template_name'] = 'sky_visitor/forgot_password_email.html'
        kwargs['token_view_name'] = 'forgot_password_change'
        kwargs['domain'] = domain
        kwargs['subject'] = "Password reset for %s" % domain
        return kwargs

    def get_success_url(self):
        return reverse('forgot_password_check_email')


class ForgotPasswordChangeView(TokenValidateMixin, FormView):
    form_class = SetPasswordForm
    template_name = 'sky_visitor/forgot_password_change.html'
    invalid_token_message = _("Invalid reset password link. Please reset your password again.")
    auto_login_on_success = True

    def get_form_kwargs(self):
        kwargs = super(ForgotPasswordChangeView, self).get_form_kwargs()
        kwargs['user'] = self.get_user_from_token()  # Form expects this
        return kwargs

    def get_form(self, form_class):
        if self.is_token_valid:
            return super(ForgotPasswordChangeView, self).get_form(form_class)
        else:
            return None

    def form_valid(self, form):
        if self.is_token_valid:
            form.save()
            auto_login(self.request, self.get_user_from_token())
        return super(ForgotPasswordChangeView, self).form_valid(form)

    def get_success_url(self):
        if not self.success_url:
            return settings.LOGIN_REDIRECT_URL


class ProfileEditView(UpdateView):
    model = User
    form_class = ProfileEditForm
    success_message = _("Profile succesfully updated.")

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, self.success_message, fail_silently=True)
        return super(ProfileEditView, self).form_valid(form)
