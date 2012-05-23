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

import uuid
import datetime
from django.contrib.auth import models as auth_models
from django.db.models.query_utils import Q
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

# Truncate the UUID for usernames a bit shorter so it is easier to use as a slug if needed
from django.core.exceptions import ValidationError

USERNAME_LENGTH = 10


def get_uuid_username_string():
    return str(uuid.uuid4().int)[:USERNAME_LENGTH]


def get_uuid_username():
    username = get_uuid_username_string()
    try:
        # We use AuthUser here because it's more straight forward and we don't need to check the subclassed user since we just need a count
        while auth_models.User.objects.get(username=username).count() > 0:
            username = get_uuid_username_string()
    except auth_models.User.DoesNotExist:
        pass
    return username


class UserManager(auth_models.UserManager):
    pass


class ExtendedUser(auth_models.User):
    """
    This is the abstract base class that you should subclass from to add your own fields.
    """
    _is_email_only = False

    # Redefining objects is needed because of our subclassing. Weird quirk. Any subclass of this model also needs to define BaseUserManager as well.
    objects = UserManager()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        super(ExtendedUser, self).save(*args, **kwargs)


class EmailUserManager(UserManager):

    def create_user(self, username, email=None, password=None):
        """
        Squash the normal create_user method and use our create_user_by_email method.

        Username will be ignored unless email is None, then username will be used as the email address
        """
        if email is None and '@' in username:
            email = username
        return self.create_user_by_email(email=email, password=password)

    def create_user_by_email(self, email, password=None):
        """
        Creates and saves a User with the given username, e-mail and password.
        """
        username = None  # Set to None here, automatically set in the model save method
        now = timezone.now()
        if not email:
            raise ValueError('An email address must be set')
        email = EmailUserManager.normalize_email(email)
        user = self.model(username=username, email=email,
                          is_staff=False, is_active=True, is_superuser=False,
                          last_login=now, date_joined=now)
        user.set_password(password)
        user.save(using=self._db)
        return user


class EmailExtendedUser(ExtendedUser):
    """
    Inherit fromt his class if you'd like to have an "email only" user and hide usernames
    """
    _is_email_only = True
    validate_email_uniqueness = True
    error_messages = {
        'unique_email': _("This email address is already in use. Please supply a different email address."),
    }

    # Redefining objects is needed because of our subclassing. Weird quirk. Any subclass of this model also needs to define BaseUserManager as well.
    objects = EmailUserManager()

    def __unicode__(self):
        return self.email

    class Meta:
        abstract = True

    def save(self, allow_email_uniqueness_validation=True, *args, **kwargs):
        if not self.pk and not self.username:
            self.username = get_uuid_username()
        if allow_email_uniqueness_validation:
            self.validate_email_is_unique()
        super(EmailExtendedUser, self).save(*args, **kwargs)

    def validate_email_is_unique(self, force_validation=False):
        from sky_visitor.utils import SubclassedUser as User
        if self.validate_email_uniqueness or force_validation:
            if User.objects.filter(email__iexact=self.email).exclude(id=self.id).exists():
                raise ValidationError({'email': self.error_messages['unique_email']})

    def clean(self):
        """
        Validate uniqueness of the email address here. If you're concerned about the extra query and any perforamce issues,
        you can disable this by settings `validate_email_uniqueness` to False and handling uniqueness yourself.
        """
        self.validate_email_is_unique()
