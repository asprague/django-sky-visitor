from extended_auth.forms import LoginForm, RegisterForm
from django.test import TestCase
from extended_auth.utils import SubclassedUser as User
from django.contrib.auth.models import User as AuthUser



class BaseTestCase(TestCase):
    pass


class TestLoginForm(BaseTestCase):
    view_url = '/user/login/'

    def test_login_form_should_be_username_based(self):
        response = self.client.get(self.view_url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context_data['form'], LoginForm)





class TestUsernameRegister(TestEmailRegister):
    view_url = '/user/register/'

    def test_register_view_should_be_username_based(self):
        response = self.client.get(self.view_url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context_data['form'], RegisterForm)

    def test_registration_should_succeed(self):
        testuser_username = 'test'
        data = {
            'username': testuser_username,
            'email': 'test@example.com',
            'password1': 'asdfasdf',
            'password2': 'asdfasdf',
        }
        response = self.client.post(self.view_url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        # Should redirect to '/' (LOGIN_REDIRECT_URL)
        self.assertRedirects(response, '/')
        self.assertEqual(User.objects.filter(username=testuser_username).count(), 1)
        self.assertEqual(AuthUser.objects.filter(username=testuser_username).count(), 1)

    def test_registration_should_fail_on_mismatched_password(self):
        data = {
            'username': 'test',
            'email': 'test@example.com',
            'password1': 'asdfasdf',
            'password2': 'mismatch',
        }
        response = self.client.post(self.view_url, data=data)
        self.assertEqual(response.status_code, 200)
        form = response.context_data['form']
        # Form should have errors for mismatched password
        self.assertEqual(len(form.errors), 1)
        self.assertIn('password2', form.errors)



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

        data = {'email': USER_EMAIL}
        response = self.client.post('/user/forgot_password/', data, follow=True)
        # Should redirect to the check email page
        self.assertRedirects(response, '/user/forgot_password/check_email/')
        # Should send the message
        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        # Should be sent to the right person
        self.assertIn(USER_EMAIL, message.to)
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
        user = AuthUser.objects.get(email=USER_EMAIL)
        # Should redirect to '/' (LOGIN_REDIRECT_URL)
        self.assertRedirected(response, '/')
        # Should have a new password
        self.assertTrue(user.check_password(new_pass))
        # Should automatically log the user in
        self.assertLoggedIn(user, backend='extended_auth.backends.BaseBackend')

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
