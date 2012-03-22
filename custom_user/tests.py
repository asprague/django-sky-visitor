from django.core.exceptions import ValidationError
from django.test import TestCase

from custom_user.models import *
from custom_user.forms import InvitationForm
from django.contrib.auth.models import User as AuthUser
from custom_user.utils import SubclassedUser as User
from custom_user.forms import UniqueRequiredEmailField


class BaseTestCase(TestCase):
    pass


class UniqueEmailTest(BaseTestCase):
    def should_error_on_duplicate_email(self):
        nonunique_email = 'nonunique@example.com'
        first_user = User.objects.create_user(nonunique_email, password='asdf')
        field = UniqueRequiredEmailField()

        self.assertRaises(ValidationError, field.clean, nonunique_email)


class InviteUserTests(BaseTestCase):

    def setUp(self):
        pass


