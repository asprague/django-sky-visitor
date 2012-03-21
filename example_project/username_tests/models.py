from custom_user.models import CustomUser, UserManager

class User(CustomUser):
    """
    Custom user class
    """

    # Needed because of our subclassing. Weird quirk.
    objects = UserManager()
