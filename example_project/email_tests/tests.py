from example_project.tests import TestRegister, TestLoginFormMixin, FIXTURE_USER_DATA, BaseTestCase, TestForgotPasswordProcess
from extended_auth.forms import EmailLoginForm, EmailRegisterForm
from django.contrib.auth.models import User as AuthUser
from django.test import TestCase
from extended_auth.utils import SubclassedUser

TestEmailForgotPasswordProcess = TestForgotPasswordProcess


class BaseEmailTestCase(BaseTestCase):
    pass


class TestEmailRegister(TestRegister):

    def get_test_data(self):
        data = super(TestEmailRegister, self).get_test_data()
        del data['username']
        return data

    def test_register_view_exists(self):
        response = super(TestEmailRegister, self).test_register_view_exists()
        form = response.context_data['form']
        self.assertIsInstance(form, EmailRegisterForm)

    def test_registration_should_succeed(self):
        super(TestEmailRegister, self).test_registration_should_succeed()
        self.assertEqual(SubclassedUser.objects.filter(email=self.get_test_data()['email']).count(), 1)

    def test_registration_should_fail_on_duplicate_email(self):
        testuser_email = 'testuser1@example.com'
        data1 = self.get_test_data()
        data1['email'] = testuser_email
        response1 = self.client.post(self.view_url, data=data1, follow=True)
        self.assertEqual(response1.status_code, 200)
        # Test user should exist
        self.assertEqual(SubclassedUser.objects.filter(email=testuser_email).count(), 1)
        self.assertEqual(AuthUser.objects.filter(email=testuser_email).count(), 1)

        data2 = data1
        response2 = self.client.post(self.view_url, data=data2, follow=True)
        self.assertEqual(response2.status_code, 200)
        form = response2.context_data['form']
        # Form should have errors for the duplicate email
        self.assertEqual(len(form.errors), 1)
        self.assertIn('email', form.errors)

        # Test user should only be in the database one time
        self.assertEqual(SubclassedUser.objects.filter(email=testuser_email).count(), 1)
        self.assertEqual(AuthUser.objects.filter(email=testuser_email).count(), 1)


class TestEmailLoginForm(TestLoginFormMixin, BaseEmailTestCase):

    def test_login_form_should_be_email_based(self):
        response = self.client.get(self.view_url)
        self.assertEqual(response.status_code, 200)
        form = response.context_data['form']
        self.assertIsInstance(form, EmailLoginForm)

    def test_login_form_should_succeed(self):
        data = FIXTURE_USER_DATA
        response = self.client.post(self.view_url, data)
        user = SubclassedUser.objects.get(email=data['email'])
        # Should be logged in
        self.assertLoggedIn(user, backend='extended_auth.backends.EmailBackend')
        # Should redirect
        self.assertRedirected(response, '/')
