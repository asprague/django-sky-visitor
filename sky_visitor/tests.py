# Copyright 2012 Concentric Sky, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.contrib.auth.models import User as AuthUser
from django.utils.unittest.case import skipUnless
from sky_visitor import utils
from sky_visitor.utils import SubclassedUser as User
from sky_visitor.forms import UniqueRequiredEmailField

subclassed_user_only_test = skipUnless(utils.is_subclassed_user(), "Only test these if configured in an sky_visitor subclassed user mode")
username_user_only_test = skipUnless(utils.is_username_user(), "Only test these if configured in username-based user mode")
email_user_only_test = skipUnless(utils.is_email_only(), "Only test these if configured in email-based user mode")
auth_user_only_test = skipUnless(utils.is_auth_user(), "Only test these if configured in auth.User")


class BaseTestCase(TestCase):
    pass

@email_user_only_test
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


@email_user_only_test
class EmailCreateUserTest(BaseTestCase):

    def test_should_create_user_with_auto_username(self):
        email = 'newuser@example.com'
        User.objects.create_user(email, password='fake')
        # Retrieve it from the DB to make sure it is fresh and clean
        user = User.objects.get(email=email)
        self.assertNotEqual(user.username, email)
        self.assertEqual(user.email, email)

    def test_should_create_user_with_auto_username_alternate(self):
        email = 'newuser@example.com'
        User.objects.create_user('notused@example.com', email=email, password='fake')
        # Retrieve it from the DB to make sure it is fresh and clean
        user = User.objects.get(email=email)
        self.assertNotEqual(user.username, email)
        self.assertEqual(user.email, email)

    def test_should_create_user_by_email_with_auto_username(self):
        email = 'newuser@example.com'
        User.objects.create_user_by_email(email, 'fake')
        # Retrieve it from the DB to make sure it is fresh and clean
        user = User.objects.get(email=email)
        self.assertNotEqual(user.username, email)
        self.assertEqual(user.email, email)


class InviteUserTests(BaseTestCase):

    def setUp(self):
        pass
