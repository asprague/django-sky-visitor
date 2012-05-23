from example_project.tests import TestRegister, FIXTURE_USER_DATA, TestForgotPasswordProcess, TestLoginFormBase
from sky_visitor.forms import LoginForm, RegisterForm
from django.test import TestCase
from sky_visitor.utils import SubclassedUser
from django.contrib.auth.models import User as AuthUser


TestUsernameForgotPasswordProcess = TestForgotPasswordProcess


class TestUsernameLoginForm(TestLoginFormBase):

    def test_login_form_should_be_username_based(self):
        response = self.client.get(self.view_url)
        self.assertEqual(response.status_code, 200)
        form = response.context_data['form']
        self.assertIsInstance(form, LoginForm)

    def test_login_form_should_succeed(self):
        data = FIXTURE_USER_DATA
        response = self.client.post(self.view_url, data)
        user = SubclassedUser.objects.get(email=data['email'])
        # Should be logged in
        self.assertLoggedIn(user, backend='sky_visitor.backends.UsernameBackend')
        # Should redirect
        self.assertRedirected(response, '/')



class TestUsernameRegister(TestRegister):

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
        self.assertEqual(SubclassedUser.objects.filter(username=testuser_username).count(), 1)
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


