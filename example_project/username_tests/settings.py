from example_project.settings import *

###
#
#   Settings specific to sky_visitor
#
###

SKY_VISITOR_USER_MODEL = 'username_tests.User'
AUTHENTICATION_BACKENDS = [
    'sky_visitor.backends.UsernameBackend',
]

INSTALLED_APPS = [
    'username_tests',
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