from example_project.settings import *

###
#
#   Settings specific to extended_auth
#
###

EXTENDED_AUTH_USER_MODEL = 'username_tests.User'
AUTHENTICATION_BACKENDS = [
    'extended_auth.backends.UsernameBackend',
]

INSTALLED_APPS = [
    'username_tests',
    'extended_auth',

    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
]


TESTS_TO_RUN = [
    'extended_auth',
    'username_tests.TestUsernameLoginForm',
    'username_tests.TestUsernameRegister',
    'username_tests.TestUsernameForgotPasswordProcess',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db-username.sqlite3',
    }
}