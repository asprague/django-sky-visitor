from custom_user.forms import EmailLoginForm
from django.conf import settings
from django.contrib.auth.models import User as AuthUser
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils.http import int_to_base36
from example_project.models import User

USER_EMAIL = 'user@example.com'
USER_PASS = 'adminadmin'

# TODO TEST: create_user process works with create_user and create_user_by_email
# TODO TEST: That unique email addresses are enforced at the model create level


class BaseTestCase(TestCase):

    def assertLoggedIn(self, user, backend=None):
        self.assertEqual(self.client.session['_auth_user_id'], user.id)
        if backend:
            self.assertEqual(self.client.session['_auth_user_backend'], backend)

    def assertRedirected(self, response, expected_url, status_code=302):
        self.assertEqual(response.status_code, status_code)
        self.assertEqual(response._headers['location'][1], 'http://testserver%s' % expected_url)

    @property
    def default_user(self):
        if not hasattr(self, '_user'):
            self._user = User.objects.get(email=USER_EMAIL)
        return self._user

class TestEmailLoginForm(BaseTestCase):

    def test_login_form_should_be_email_based(self):
        response = self.client.get('/user/login/')
        self.assertEqual(response.status_code, 200)
        form = response.context_data['form']
        self.assertIsInstance(form, EmailLoginForm)

    def test_login_form_should_succeed(self):
        data = {
            'email': USER_EMAIL,
            'password': USER_PASS,
        }
        response = self.client.post('/user/login/', data)
        user = User.objects.get(email=USER_EMAIL)
        # Should be logged in
        self.assertLoggedIn(user, backend='custom_user.backends.EmailBackend')
        # Should redirect
        self.assertRedirected(response, '/')


class TestForgotPasswordProcess(BaseTestCase):

    # TODO TEST: If an invalid email is entered into the forgot password form
    # TODO TEST: Token should be invalid after it is used once
    # TODO TEST: Token older than X weeks (will require removing hard coded reset URL)


    def _get_token_url(self, user=None, with_host=True):
        if user is None:
            user = self.default_user
        url = reverse('forgot_password_change', kwargs={'uidb36':int_to_base36(user.id), 'token': default_token_generator.make_token(user)})
        if  with_host:
            url = 'http://testserver%s' % url
        return url

    def test_forgot_password_form_should_send_email(self):
        response = self.client.get('/user/forgot_password/')
        self.assertEqual(response.status_code, 200)

        data = {'email': USER_EMAIL}
        response = self.client.post('/user/forgot_password/', data, follow=True)
        # Should redirect to the check email page
        self.assertRedirects(response, '/user/forgot_password/check_email/')
        # Should send the message
        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        # Should have the correct subject
        self.assertEqual(message.subject, 'Password reset for testserver')
        # Should have the link in the body of the message
        self.assertIn(self._get_token_url(), message.body)
        # TODO TEST: Email was sent to the right person
        # TODO TEST: That the link works and lands you on the right page

    def test_reset_password_form_should_success_with_valid_input(self):
        response = self.client.get(self._get_token_url())
        self.assertEqual(response.status_code, 200)

        new_pass = 'asdfasdf'
        data = {
            'new_password1': new_pass,
            'new_password2': new_pass,
        }
        response = self.client.post(self._get_token_url(), data)
        user = AuthUser.objects.get(email=USER_EMAIL)
        # Should redirect to '/'
        self.assertRedirected(response, '/')
        # Should have a new password
        self.assertTrue(user.check_password(new_pass))
        # Should automatically log the user in
        self.assertLoggedIn(user, backend='custom_user.backends.BaseBackend')

    def test_reset_password_form_should_fail_with_invalid_token(self):
        # Should work fine for normal URL
        response = self.client.get(self._get_token_url())
        self.assertEqual(response.status_code, 200)
        # User ID of this token is modified
        response = self.client.get('http://testserver/user/forgot_password/2-35t-d4e092280eb134000672/', follow=True)
        self.assertRedirects(response, '/user/login/')
        # Token modified
        response = self.client.get('http://testserver/user/forgot_password/1-35t-d4e092280eb134000671/', follow=True)
        self.assertRedirects(response, '/user/login/')

