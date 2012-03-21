"""
Default settings. See __init__.py for code that injects these defaults
"""

# This must be set to the python path (not including .models) of your primary subclass of User.
# Also, custom_user.models.User will always contain this class as a shortcut
CUSTOM_USER_MODEL = None

# This setting is used only if your user model inherits from CustomUser rather than EmailCustomUser. If you use CustomUser directly,
# and this settings is true, then the default forms will show email forms intead of login forms.
CUSTOM_USER_EMAIL_LOGIN = False

# The URL to redirect to after logging a user in (or after they reset their password and are auto-logged in)
CUSTOM_USER_AFTER_LOGIN_REDIRECT_URL = '/'