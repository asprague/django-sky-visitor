from extended_auth.forms import LoginForm, RegisterForm
from django.test import TestCase


class BaseTestCase(TestCase):
    pass


class TestLoginForm(BaseTestCase):
    view_url = '/user/login/'

    def test_login_form_should_be_username_based(self):
        response = self.client.get(self.view_url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context_data['form'], LoginForm)


class TestUsernameRegister(BaseTestCase):
    view_url = '/user/register/'

    def test_register_view_should_be_username_based(self):
        response = self.client.get(self.view_url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context_data['form'], RegisterForm)
