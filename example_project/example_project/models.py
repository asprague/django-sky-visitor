from custom_user.models import CustomUser, EmailUserManager

class FallbackUser(CustomUser):
    """
    Shouldn't really need this class. Here mostly for testing purposes. Instead, you should subclass CustomUser
    in your application and specify it using the CUSTOM_USER_MODEL setting
    """

    # Needed because of our subclassing. Weird quirk.
    objects = EmailUserManager()