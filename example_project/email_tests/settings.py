from example_project.settings import *

###
#
#   Settings specific to extended_auth
#
###

EXTENDED_AUTH_USER_MODEL = 'email_tests.User'
AUTHENTICATION_BACKENDS = [
    'extended_auth.backends.EmailBackend',
]


INSTALLED_APPS = [
    'email_tests',
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
    'email_tests.TestEmailLoginForm',
    'email_tests.TestEmailRegister',
    'email_tests.TestEmailForgotPasswordProcess',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db-email.sqlite3',
    }
}