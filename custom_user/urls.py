from django.conf.urls import *
from django.views.generic.base import TemplateView
from custom_user.views import *

CUSTOM_USER_TOKEN_REGEX = '(?P<uidb36>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})'

urlpatterns = patterns('',
    url(r'^register/$',                         RegisterView.as_view(),         name='register'),
    url(r'^login/$',                            LoginView.as_view(),            name='login'),
    url(r'^logout/$',                           LogoutView.as_view(),           name='logout'),
#    url(r'invitation/%s/$' % CUSTOM_USER_TOKEN_REGEX, InvitationCompleteView.as_view(),   name='invitation_complete'),
#    url(r'invitation/done/$',   InvitationDoneView.as_view(),   name='invitation_done'),
    url(r'^forgot_password/$',                  ForgotPasswordView.as_view(),   name='forgot_password'),
    url(r'^forgot_password/check_email/$',      TemplateView.as_view(template_name='custom_user/forgot_password_check_email.html'), name='forgot_password_check_email'),
    url(r'^forgot_password/%s/$' % CUSTOM_USER_TOKEN_REGEX, ForgotPasswordChangeView.as_view(),     name='forgot_password_change'),
)
