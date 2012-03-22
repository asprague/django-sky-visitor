from custom_user.forms import EmailLoginForm
from django.conf import settings
from django.contrib.auth.models import User as AuthUser
from django.core import mail
from django.core.urlresolvers import reverse
from django.test import TestCase

USER_EMAIL = 'user@example.com'
USER_PASS = 'adminadmin'
USER_RESET_URL = 'http://testserver/user/forgot_password/1-35t-d4e092280eb134000672/'

class BaseTestCase(TestCase):
    pass


# TODO TEST: create_user process works with create_user and create_user_by_email
# TODO TEST: That unique email addresses are enforced at the model create level


class TestEmailLoginForm(BaseTestCase):

    def test_login_form_should_be_email_based(self):
        response = self.client.get('/user/login/')
        self.assertEqual(response.status_code, 200)
        form = response.context_data['form']
        self.assertIsInstance(form, EmailLoginForm)



class TestForgotPasswordProcess(BaseTestCase):

    # TODO TEST: If an invalid email is entered into the forgot password form
    # TODO TEST: Token should be invalid after it is used once
    # TODO TEST: token older than X weeks (will require removing hard coded reset URL=

    def test_forgot_password_form_should_send_email(self):
        response = self.client.get('/user/forgot_password/')
        self.assertEqual(response.status_code, 200)

        data = {'email': USER_EMAIL}
        response = self.client.post('/user/forgot_password/', data, follow=True)
        self.assertRedirects(response, '/user/forgot_password/check_email/')
        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertEqual(message.subject, 'Password reset for testserver')
        self.assertIn(USER_RESET_URL, message.body)

    def test_reset_password_form_should_success_with_valid_input(self):
        response = self.client.get(USER_RESET_URL)
        self.assertEqual(response.status_code, 200)

        new_pass = 'asdfasdf'
        data = {
            'new_password1': new_pass,
            'new_password2': new_pass,
        }
        response = self.client.post(USER_RESET_URL, data)
        # Should redirect to '/'
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response._headers['location'][1], 'http://testserver/')
        user = AuthUser.objects.get(email=USER_EMAIL)
        # Should have a new password
        self.assertTrue(user.check_password(new_pass))
        # Should automatically log the user in
        self.assertEqual(self.client.session['_auth_user_id'], user.id)
        self.assertEqual(self.client.session['_auth_user_backend'], 'custom_user.backends.BaseBackend')

    def test_reset_password_form_should_fail_with_invalid_token(self):
        # Should work fine for normal URL
        response = self.client.get(USER_RESET_URL)
        self.assertEqual(response.status_code, 200)
        # User ID of this token is modified
        response = self.client.get('http://testserver/user/forgot_password/2-35t-d4e092280eb134000672/', follow=True)
        self.assertRedirects(response, '/user/login/')
        # Token modified
        response = self.client.get('http://testserver/user/forgot_password/1-35t-d4e092280eb134000671/', follow=True)
        self.assertRedirects(response, '/user/login/')

