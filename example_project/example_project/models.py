from extended_auth.models import EmailUserManager, EmailExtendedUser

# This is the model that is used by default in this app.
class User(EmailExtendedUser):
    """
    ExtendedUser concrete class with email-only authentication
    """

    objects = EmailUserManager() # Needed because of our subclassing. Weird quirk.


