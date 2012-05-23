from sky_visitor.models import ExtendedUser, UserManager


class User(ExtendedUser):
    """
    ExtendedUser concrete class
    """

    # Needed because of our subclassing. Weird quirk.
    objects = UserManager()
