from django.core.exceptions import ValidationError
from django.test import TestCase
from django.contrib.auth.models import User as AuthUser
from custom_user.utils import SubclassedUser as User
from custom_user.forms import UniqueRequiredEmailField


class BaseTestCase(TestCase):
    pass


# TODO TEST: That it validates on first save
# TODO TEST: That it validates when email is changed later
# TODO TEST: That it works with create_user
# TODO TEST: That it works with create_user_by_email

class UniqueEmailTest(BaseTestCase):
    def test_should_error_on_duplicate_email_on_create(self):
        nonunique_email = 'nonunique@example.com'
        first_user = User.objects.create_user(nonunique_email, password='asdf')
        with self.assertRaises(ValidationError):
            second_user = User.objects.create_user(nonunique_email, password='asdf')

    def test_should_error_on_duplicate_email_on_update(self):
        nonunique_email = 'nonunique@example.com'
        first_user = User.objects.create_user(nonunique_email, password='asdf')
        second_user = User.objects.create_user('unique@example.com', password='asdf')
        with self.assertRaises(ValidationError):
            second_user.email = nonunique_email
            second_user.save()

    def test_should_not_error_on_duplicate_email_if_setting_overridden(self):
        nonunique_email = 'nonunique@example.com'
        User.validate_email_uniqueness = False
        first_user = User.objects.create_user(nonunique_email, password='asdf')
        # Shouldn't throw an error here
        second_user = User.objects.create_user(nonunique_email, password='asdf')


    def test_should_not_error_on_duplicate_email_if_save_argument_overridden(self):
        nonunique_email = 'nonunique@example.com'
        User.validate_email_uniqueness = True
        first_user = User.objects.create_user(nonunique_email, password='asdf')
        # Shouldn't throw an error here
        second_user = User(username='foo', email=nonunique_email, password='asdf')
        second_user.save(allow_email_uniqueness_validation=False)


class InviteUserTests(BaseTestCase):

    def setUp(self):
        pass


