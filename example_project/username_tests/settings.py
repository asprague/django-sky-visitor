from example_project.settings import *

EXTENDED_AUTH_USER_MODEL = 'username_tests.User'


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


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db2.sqlite3',
    }
}