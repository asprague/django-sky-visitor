from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.core.urlresolvers import reverse
from django.test.testcases import TestCase
from django.utils.http import int_to_base36
from django.utils.unittest.case import skipUnless
from sky_visitor import utils
from sky_visitor.forms import EmailRegisterForm, LoginForm, SetPasswordForm
from django.contrib.auth.models import User as AuthUser
from sky_visitor.tests import auth_user_only_test
from sky_visitor.utils import SubclassedUser

FIXTURE_USER_DATA = {
    'username': 'testuser',
    'email': 'testuser@example.com',
    'password': 'adminadmin'
}

class BaseTestCase(TestCase):

    @property
    def default_user(self):
        if not hasattr(self, '_default_user'):
            self._default_user = SubclassedUser.objects.get(email=FIXTURE_USER_DATA['email'])
        return self._default_user

    def assertLoggedIn(self, user, backend=None):
        self.assertEqual(self.client.session['_auth_user_id'], user.id)
        if backend:
            self.assertEqual(self.client.session['_auth_user_backend'], backend)

    def assertRedirected(self, response, expected_url, status_code=302):
        self.assertEqual(response.status_code, status_code)
        self.assertEqual(response._headers['location'][1], 'http://testserver%s' % expected_url)


class TestRegister(BaseTestCase):
    view_url = '/user/register/'

    def get_test_data(self):
        data = {
            'username': 'registeruser',
            'email': 'registeruser@example.com',
            'password1': 'asdfasdf',
            'password2': 'asdfasdf',
        }
        return data

    def test_register_view_exists(self):
        response = self.client.get(self.view_url)
        self.assertEqual(response.status_code, 200)
        return response

    def test_registration_should_succeed(self):
        data = self.get_test_data()
        testuser_email = data['email']
        response = self.client.post(self.view_url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        # Should redirect to '/' (LOGIN_REDIRECT_URL)
        self.assertRedirects(response, '/')
        self.assertEqual(AuthUser.objects.filter(email=testuser_email).count(), 1)

    def test_registration_should_fail_on_mismatched_password(self):
        data = self.get_test_data()
        data['password2'] = 'mismatch'
        response = self.client.post(self.view_url, data=data)
        self.assertEqual(response.status_code, 200)
        form = response.context_data['form']
        # Form should have errors for mismatched password
        self.assertEqual(len(form.errors), 1)
        self.assertIn('password2', form.errors)


class TestLoginFormBase(BaseTestCase):
    view_url = '/user/login/'

    def test_login_form_should_exist(self):
        response = self.client.get(self.view_url)
        self.assertEqual(response.status_code, 200)

    def test_login_form_should_succeed(self):
        data = FIXTURE_USER_DATA
        response = self.client.post(self.view_url, data)
        # Should redirect
        self.assertRedirected(response, '/')


class TestAuthUserLoginForm(TestLoginFormBase):

    def test_auth_user_should_have_username_form(self):
        response = self.client.get(self.view_url)
        self.assertEqual(response.status_code, 200)
        form = response.context_data['form']
        self.assertIsInstance(form, LoginForm)

    def test_login_form_should_succeed(self):
        super(TestAuthUserLoginForm, self).test_login_form_should_succeed()
        data = {
            'username': FIXTURE_USER_DATA['username'],
            'password': FIXTURE_USER_DATA['password'],
        }
        # Should be logged in
        user = AuthUser.objects.get(username=data['username'])
        self.assertLoggedIn(user, backend='django.contrib.auth.backends.ModelBackend')


class TestForgotPasswordProcess(BaseTestCase):

    # TODO TEST: Token older than X weeks (will require removing hard coded reset URL)

    def _get_password_reset_url(self, user=None, with_host=True):
        if user is None:
            user = self.default_user
        url = reverse('forgot_password_change', kwargs={'uidb36': int_to_base36(user.id), 'token': default_token_generator.make_token(user)})
        if  with_host:
            url = 'http://testserver%s' % url
        return url

    def test_forgot_password_form_should_send_email(self):
        response = self.client.get('/user/forgot_password/')
        self.assertEqual(response.status_code, 200)

        data = {'email': FIXTURE_USER_DATA['email']}
        response = self.client.post('/user/forgot_password/', data, follow=True)
        # Should redirect to the check email page
        self.assertRedirects(response, '/user/forgot_password/check_email/')
        # Should send the message
        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        # Should be sent to the right person
        self.assertIn(data['email'], message.to)
        # Should have the correct subject
        self.assertEqual(message.subject, 'Password reset for testserver')
        # Should have the link in the body of the message
        self.assertIn(self._get_password_reset_url(), message.body)
        # Link in email should work and land you on a set password form
        response2 = self.client.get(self._get_password_reset_url())
        self.assertIsInstance(response2.context_data['form'], SetPasswordForm)

    def test_reset_password_form_should_success_with_valid_input(self):
        response = self.client.get(self._get_password_reset_url())
        # Should succeed and have the appropraite form on the page
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context_data['form'], SetPasswordForm)

        new_pass = 'asdfasdf'
        data = {
            'new_password1': new_pass,
            'new_password2': new_pass,
        }
        response = self.client.post(self._get_password_reset_url(), data)
        user = AuthUser.objects.get(email=FIXTURE_USER_DATA['email'])
        # Should redirect to '/' (LOGIN_REDIRECT_URL)
        self.assertRedirected(response, '/')
        # Should have a new password
        self.assertTrue(user.check_password(new_pass))
        # Should automatically log the user in
        self.assertLoggedIn(user, backend='sky_visitor.backends.BaseBackend')

        # Now log the user out and make sure that reset link doesn't work anymore
        self.client.logout()
        response2 = self.client.get(self._get_password_reset_url(), follow=True)
        self.assertRedirects(response2, '/user/login/')

    def test_reset_password_form_should_fail_with_invalid_token(self):
        # Should work fine for normal URL
        response = self.client.get(self._get_password_reset_url())
        self.assertEqual(response.status_code, 200)
        # User ID of this token is modified
        response = self.client.get('http://testserver/user/forgot_password/2-35t-d4e092280eb134000672/', follow=True)
        self.assertRedirects(response, '/user/login/')
        # Token modified
        response = self.client.get('http://testserver/user/forgot_password/1-35t-d4e092280eb134000671/', follow=True)
        self.assertRedirects(response, '/user/login/')
