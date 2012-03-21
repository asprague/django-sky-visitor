from custom_user.models import CustomUser, EmailUserManager, UserManager, EmailCustomUser

# This is the model that is used by default in this app.
class User(EmailCustomUser):
    """
    Custom user class with email-only authentication
    """

    objects = EmailUserManager() # Needed because of our subclassing. Weird quirk.



# This model is used in tests, but isn't specified in the settings for the normal use of this example project
class OtherUser(CustomUser):
    """
    Custom user class
    """

    # Needed because of our subclassing. Weird quirk.
    objects = UserManager()
