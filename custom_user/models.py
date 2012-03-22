import uuid
import datetime
from django.contrib.auth import models as auth_models

# Truncate the UUID for usernames a bit shorter so it is easier to use as a slug if needed
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

class CustomUser(auth_models.User):
    """
    This is the abstract base class that you should subclass from to add your own fields.
    """
    _is_email_only = False

    # Redefining objects is needed because of our subclassing. Weird quirk. Any subclass of this model also needs to define BaseUserManager as well.
    objects = UserManager()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.pk:
            self._newly_created = True
        super(CustomUser, self).save(*args, **kwargs)



class EmailUserManager(UserManager):

    def create_user(self, username, email=None, password=None):
        """
        Squash the normal create_user method and use our create_user_by_email method.

        Username will be ignored unless email is None, then username will be used as the email address
        """
        if email is None and '@' in username:
            email = username
        return self.create_user_by_email(email=email, password=password)

    def create_user_by_email(self, email, password=None, commit=True):
        """
        Creates and saves a User with the given username, e-mail and password.
        """
        username = None
        now = datetime.datetime.now()

        # Normalize the address by lowercasing the domain part of the email
        # address.
        try:
            email_name, domain_part = email.strip().split('@', 1)
        except ValueError:
            pass
        else:
            email = '@'.join([email_name, domain_part.lower()])

        user = self.model(username=username, email=email, is_staff=False,
                         is_active=True, is_superuser=False, last_login=now,
                         date_joined=now)

        user.set_password(password)
        if commit:
            user.save(using=self._db)
        return user

class EmailCustomUser(CustomUser):
    """
    Inherit fromt his class if you'd like to have an "email only" user and hide usernames
    """
    _is_email_only = True

    # Redefining objects is needed because of our subclassing. Weird quirk. Any subclass of this model also needs to define BaseUserManager as well.
    objects = EmailUserManager()

    def __unicode__(self):
        return self.email

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.pk and not self.username:
            self.username = get_uuid_username()
        super(EmailCustomUser, self).save(*args, **kwargs)





