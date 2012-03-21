from custom_user.forms import EmailLoginForm, LoginForm
from custom_user.views import LoginView
from django.conf import settings
from django.core import mail
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import RequestFactory
from django.test.utils import override_settings

ADMIN_EMAIL = 'admin@admin.com'

class BaseTestCase(TestCase):
    pass


class TestEmailLoginForm(BaseTestCase):

    def test_login_form_should_be_email_based(self):
        response = self.client.get('/user/login/')
        self.assertEqual(response.status_code, 200)
        form = response.context_data['form']
        self.assertIsInstance(form, EmailLoginForm)

    # TODO TEST: Login process works

class TestForgotPasswordForm(BaseTestCase):

    def test_forgot_password_form(self):
        response = self.client.get('/user/forgot_password/')
        self.assertEqual(response.status_code, 200)

        data = {'email': ADMIN_EMAIL}
        response = self.client.post('/user/forgot_password/', data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, '/user/forgot_password/check_email/')
        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertEqual(message.subject, 'Password reset on testserver')
        url = "http://testserver/user/forgot_password/1-35t-5af9e199449e388d0982/"
        self.assertIn(url, message.body)