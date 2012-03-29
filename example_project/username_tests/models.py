from extended_auth.models import ExtendedUser, UserManager


class User(ExtendedUser):
    """
    ExtendedUser concrete class
    """

    # Needed because of our subclassing. Weird quirk.
    objects = UserManager()
