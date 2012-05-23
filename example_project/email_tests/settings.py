from example_project.settings import *

###
#
#   Settings specific to sky_visitor
#
###

SKY_VISITOR_USER_MODEL = 'email_tests.User'
AUTHENTICATION_BACKENDS = [
    'sky_visitor.backends.EmailBackend',
]


INSTALLED_APPS = [
    'email_tests',
    'sky_visitor',

    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
]

TESTS_TO_RUN = [
    'sky_visitor',
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