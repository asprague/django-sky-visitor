from django.contrib.auth.tokens import PasswordResetTokenGenerator


# We can re-use the password reset token generator to generate URLs for activating accounts. Requires that SECRET_KEY is
# set in settings.
default_token_generator = PasswordResetTokenGenerator()