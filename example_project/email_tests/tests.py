from example_project.tests import TestRegister
from extended_auth.forms import EmailLoginForm, EmailRegisterForm
from django.contrib.auth.models import User as AuthUser
from django.test import TestCase
from extended_auth.utils import SubclassedUser

USER_USERNAME = 'testuser'
USER_EMAIL = 'testuser@example.com'
USER_PASS = 'adminadmin'


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
            self._user = SubclassedUser.objects.get(email=USER_EMAIL)
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
        user = SubclassedUser.objects.get(email=USER_EMAIL)
        # Should be logged in
        self.assertLoggedIn(user, backend='extended_auth.backends.EmailBackend')
        # Should redirect
        self.assertRedirected(response, '/')


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