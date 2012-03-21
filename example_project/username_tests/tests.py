from custom_user.forms import EmailLoginForm, LoginForm
from django.conf import settings
from django.test import TestCase
from example_project.tests import BaseTestCase


class TestLoginForm(BaseTestCase):

    def test_login_form_should_be_username_based(self):
        response = self.client.get('/user/login/')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context_data['form'], LoginForm)
