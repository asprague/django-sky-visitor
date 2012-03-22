from custom_user.forms import EmailLoginForm, LoginForm
from custom_user.views import LoginView
from django.conf import settings
from django.contrib.auth.models import User as AuthUser
from django.core import mail
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import RequestFactory
from django.test.utils import override_settings

ADMIN_EMAIL = 'admin@admin.com'
ADMIN_PASS = 'admin'
ADMIN_RESET_URL = 'http://testserver/user/forgot_password/1-35t-5af9e199449e388d0982/'

class BaseTestCase(TestCase):
    pass


class TestEmailLoginForm(BaseTestCase):

    def test_login_form_should_be_email_based(self):
        response = self.client.get('/user/login/')
        self.assertEqual(response.status_code, 200)
        form = response.context_data['form']
        self.assertIsInstance(form, EmailLoginForm)

    # TODO TEST: Login process works


class TestForgotPasswordProcess(BaseTestCase):

    def test_forgot_password_form_should_send_email(self):
        response = self.client.get('/user/forgot_password/')
        self.assertEqual(response.status_code, 200)

        data = {'email': ADMIN_EMAIL}
        response = self.client.post('/user/forgot_password/', data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, '/user/forgot_password/check_email/')
        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertEqual(message.subject, 'Password reset for testserver')
        self.assertIn(ADMIN_RESET_URL, message.body)

    def test_reset_password_form_should_success_with_valid_input(self):
        response = self.client.get(ADMIN_RESET_URL)
        self.assertEqual(response.status_code, 200)

        new_pass = 'asdfasdf'
        data = {
            'new_password1': new_pass,
            'new_password2': new_pass,
        }
        response = self.client.post(ADMIN_RESET_URL, data)
        # Should redirect to '/'
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response._headers['location'][1], 'http://testserver/')
        user = AuthUser.objects.get(email=ADMIN_EMAIL)
        # Should have a new password
        self.assertTrue(user.check_password(new_pass))
        # Should automatically log the user in
        self.assertEqual(self.client.session['_auth_user_id'], user.id)
        self.assertEqual(self.client.session['_auth_user_backend'], 'custom_user.backends.BaseBackend')

    def test_reset_password_form_should_fail_with_invalid_token(self):
        # Should work fine for normal URL
        response = self.client.get(ADMIN_RESET_URL)
        self.assertEqual(response.status_code, 200)
        # User ID of this token is modified
        response = self.client.get('http://testserver/user/forgot_password/2-35t-5af9e199449e388d0982/', follow=True)
        self.assertRedirects(response, '/user/login/')
        # Token modified
        response = self.client.get('http://testserver/user/forgot_password/1-35t-5af9e199449e388d0981/', follow=True)
        self.assertRedirects(response, '/user/login/')

