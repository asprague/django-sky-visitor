from custom_user.forms import EmailLoginForm, LoginForm
from custom_user.views import LoginView
from django.conf import settings
from django.test import TestCase
from django.test.client import RequestFactory
from django.test.utils import override_settings

class BaseTestCase(TestCase):
    pass


class TestEmailLoginForm(BaseTestCase):

    def test_login_form_should_be_email_based(self):
        response = self.client.get('/user/login/')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context_data['form'], EmailLoginForm)
