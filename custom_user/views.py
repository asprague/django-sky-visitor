import urlparse
from custom_user.emails import TokenTemplateEmail
from django.contrib import messages
from django.contrib.auth import REDIRECT_FIELD_NAME, login, logout
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import get_current_site
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.template import loader
from django.template.context import Context
from django.utils.decorators import method_decorator
from django.utils.http import base36_to_int, int_to_base36
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.generic.base import RedirectView
from django.views.generic.edit import FormView, UpdateView
from custom_user.backends import auto_login
from custom_user.forms import EmailLoginForm, InvitationForm, SetPasswordForm, InvitationCompleteForm, ProfileEditForm, LoginForm, PasswordResetForm
from custom_user.utils import SubclassedUser as User, is_email_only
from django.conf import settings

# Originally from: https://github.com/stefanfoulis/django-class-based-auth-views/blob/develop/class_based_auth_views/views.py
class LoginView(FormView):
    """
    This is a class based version of django.contrib.auth.views.login.

    Usage:
        in urls.py:
            url(r'^login/$',
                LoginView.as_view(
                    form_class=MyCustomAuthFormClass,
                    success_url='/my/custom/success/url/),
                name="login"),

    """
    redirect_field_name = REDIRECT_FIELD_NAME
    success_url_overrides_redirect_field = False
    template_name = 'custom_user/login.html'

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
    template_name = 'custom_user/invite.html'
    # Need to define success_url or override get_success_url()
    pass


class TokenValidateMixin(object):
    token_generator = default_token_generator
    display_message_on_invalid_token = True
    is_token_valid = False

    def get_token_generator(self):
        return self.token_generator

    def dispatch(self, request, *args, **kwargs):
        uidb36 = kwargs['uidb36']
        token = kwargs['token']
        assert uidb36 is not None and token is not None # checked by URLconf
        try:
            uid_int = base36_to_int(uidb36)
            self._user = User.objects.get(id=uid_int)
        except (ValueError, User.DoesNotExist):
            self._user = None
        self.is_token_valid = (self._user is not None and self.get_token_generator().check_token(self._user, token))
        if not self.is_token_valid:
            self.token_invalid(request, *args, **kwargs)
        return super(TokenValidateMixin, self).dispatch(request, *args, **kwargs)

    def token_invalid(self, request, *args, **kwargs):
        if self.display_message_on_invalid_token:
            messages.error(request, "Invalid URL token. Your probably already have an account. Please try to login. Please return to the home page and try again.", fail_silently=True)


class InvitationCompleteView(TokenValidateMixin, UpdateView):
    form_class = InvitationCompleteForm
    form_class_set_password = SetPasswordForm
    context_object_name = 'invited_user'
    auto_login_on_success = True
    template_name = 'custom_user/invite_complete.html'
    # Since this is an UpdateView, the defautl success_url will be the user's get_absolute_url(). Override if you'd like different behavior

    def get_object(self, queryset=None):
        return self._user

    def post(self, request, *args, **kwargs):
        if self.is_token_valid:
            return super(InvitationCompleteView, self).post(request, *args, **kwargs)
        else:
            return self.get(request, *args, **kwargs)

    def token_invalid(self, request, *args, **kwargs):
        if self.display_message_on_invalid_token:
            messages.error(request, "Invalid invite URL. Please request another invite.", fail_silently=True)

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
        return super(InvitationCompleteView, self).form_valid(form) # Save and redirect

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
                    context_data['set_password_form'] = self.form_class_set_password(self._user, self.request.POST, prefix='set_password')
                else:
                    context_data['set_password_form'] = self.form_class_set_password(self._user, prefix='set_password')
        else:
            context_data['set_password_form'] = None
        return context_data


class LogoutView(RedirectView):

    def get(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, "Successfully logged out", fail_silently=True)
        return super(LogoutView, self).get(request, *args, **kwargs)

    def get_redirect_url(self, **kwargs):
        return reverse('login')


class ForgotPasswordView(SendTokenEmailMixin, FormView):
    form_class = PasswordResetForm
    template_name = 'custom_user/forgot_password_start.html'

    def form_valid(self, form):
        user = form.users_cache[0]
        self.send_email(user)
        return super(ForgotPasswordView, self).form_valid(form)  # Do redirect

    def get_email_kwargs(self, user):
        kwargs = super(ForgotPasswordView, self).get_email_kwargs(user)
        domain = self.request.get_host()
        kwargs['email_template_name'] = 'custom_user/password_reset_email.html'
        kwargs['token_view_name'] = 'forgot_password_change'
        kwargs['domain'] = domain
        kwargs['subject'] = "Password reset on %s" % domain    #get_current_site(self.request)
        return kwargs

    def get_success_url(self):
        return reverse('forgot_password_check_email')


class ForgotPasswordChangeView(TokenValidateMixin, FormView):
    form_class = SetPasswordForm
    template_name = 'custom_user/forgot_password_change.html'

    def get_form_kwargs(self):
        kwargs = super(ForgotPasswordChangeView, self).get_form_kwargs()
        kwargs['user'] = self._user  # Form expects this
        return kwargs

    def get_form(self, form_class):
        if self.is_token_valid:
            return super(ForgotPasswordChangeView, self).get_form(form_class)
        else:
            return None

    def form_valid(self, form):
        if self.is_token_valid:
            form.save()
        return super(ForgotPasswordChangeView, self).form_valid(form)

    def token_invalid(self, request, *args, **kwargs):
        if self.display_message_on_invalid_token:
            messages.error(request, "Invalid reset password link. Please reset your password again.", fail_silently=True)

class ProfileEditView(UpdateView):
    model = User
    form_class = ProfileEditForm

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Profile succesfully updated.", fail_silently=True)
        return super(ProfileEditView, self).form_valid(form)