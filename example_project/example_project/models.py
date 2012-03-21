from custom_user.models import EmailUserManager, EmailCustomUser

# This is the model that is used by default in this app.
class User(EmailCustomUser):
    """
    Custom user class with email-only authentication
    """

    objects = EmailUserManager() # Needed because of our subclassing. Weird quirk.


