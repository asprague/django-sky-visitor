from django.test.testcases import TestCase
from extended_auth.forms import EmailRegisterForm
from django.contrib.auth.models import User as AuthUser

class BaseTestCase(TestCase):
    pass

class TestRegister(BaseTestCase):
    view_url = '/user/register/'

    def get_test_data(self):
        data = {
            'username': 'test@example.com',
            'email': 'testuser@example.com',
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