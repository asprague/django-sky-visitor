A full featured authentication and user system that extends the default Django contib.auth pacakge.

**Note:** Version 0.1.0. This library is under active development. While in active development, the API will be changing frequently.


# Features

  * Subclass the User model to add your own fields, making queries easier to write
  * Class-based view implementations of all of the views
  * Email-based authentication. Entirely hides username from the user experience and allows an email-focused experience.
  * Invitations
  * Password rules

This library addresses many of the problems discussed on the Django wiki about [how to improve contrib.auth](https://code.djangoproject.com/wiki/ContribAuthImprovements).

# Usage
Throughout this app, any class beginning with `Email` indicates that it is for use with email-only authentication systems.
In all cases, there should be a matching class without `Email` at the beginning of the class name that is for use with username-focused authentication systems.


## Quickstart

  * `pip install PACKAGEPATHHERE`
  * Add `extended_auth` near the top of your `INSTALLED_APPS` setting
  * Somewhere in your own `myapp.models.py`, define one of the two following code blocks:

```python
# Assume this is in myapp.models
from extended_auth import EmailExtendedUser, EmailUserManager

class User(EmailExtendedUser):
    objects = EmailUserManager()
```

  * In your're `settings.py` add these lines:

```python

# Add this line to your INSTALLED_APPS
INSTALLED_APPS = [
    'extended_auth',
    # ...
]

# Specify a URL to redirect to after login
LOGIN_REDIRECT_URL = '/'
```

## Sublcassing User model

Add the following to your settings.py if you wish to subclass the User model:

```python
# Change myapp to the name of the app where you extend EmailExtendedUser
EXTENDED_AUTH_USER_MODEL = 'myapp.User'
AUTHENTICATION_BACKENDS = [
    'extended_auth.backends.EmailBackend',
]
```


## Advanced usage

  * Override URLs and views to provide custom workflows
  * Customize views and URLs
  * Customize forms
  * Choose to not automatically log a user in after they compelte a registration, or password reset
  * Don't create users with `manage.py createsuperuser` or `django.contrib.auth.models.User.create_user()` because there won't be a proper entry in the subclassed user table for them
  * On EmailExtendedUser you can set `validate_email_uniqeness` to false if you're concerned about the extra database query for each call to clean()

### Messages
This app uses the [messages framework](https://docs.djangoproject.com/en/dev/ref/contrib/messages/) to pass success messages
around after certain events (password reset completion, for example). If you would like to improve the experience for
your users in this way, make sure you follow the message framework docs to enable and render these messages on your site.


# Settings
Must specify `SECRET_KEY` in your settings for any emails with tokens to be secure (example: invitation, confirm email address, forgot password, etc)


# Admin
By default, we remove the admin screens for `auth.User` and place in an auth screen for you authentication

If you want to re-add the the django contrib user, you can do that by re-registering django.contrib.auth.User

If you want fine-grained control over the admin you can subclass the extended_auth `UserAdmin`:

```python
from extended_auth.admin import UserAdmin

class MyUserAdmin(UserAdmin):
   # Your code here
   pass

admin.site.register(MyUser, MyUserAdmin)
```


# Testing

Tests are broken into three separate apps running under three different "modes":

  1. "auth user" mode (default)
    * Uses `example_project/settings.py`
    * Uses `django.contrib.auth.models.User` as the user model
    * Contains most of the tests
  2. "email user" mode
    * Uses `email_tests/settings.py`
    * Uses `email_tests.models.User` (a subclass of `extended_auth.models.EmailExtendedUser`) as the user model
  2. "username user" mode
    * Uses `username_tests/settings.py`
    * Uses `username_tests.models.User` (a subclass of `extended_auth.models.ExtendedUser`) as the user model


A test runner is configured in each settings.py to run only the tests that are appropriate.

You can run the tests like so:

    cd example_project
    # "auth user" tests
    ./manage.py test
    # "email user" tests
    ./manage.py test --settings=email_tests.settings
    # Run username-based tests
    ./manage.py test --settings=username_tests.settings


# Subclassing User vs User Profiles
One of the problems this module was created to solve is the challenge presented when you want to store additional information
about the user. The Django docs [suggest](https://docs.djangoproject.com/en/dev/topics/auth/#storing-additional-information-about-users)
having a `UserProfile` model with a OneToOneField to `User`.

Subclassing the User model offers a few benefits over the `UserProfile` approach

  * `ModelForm`s will automatically include your extended fields in the forms they generate. This makes CRUD operations much easier.
  * Similarly, Django's admin pages will automatically include this fields on your subclassed user
  * In the background, Django automatically does an inner join between `contrib.auth.models.User` and your subclassed user model via
[proxy models](https://docs.djangoproject.com/en/dev/topics/db/models/#proxy-models). This is nicer than having to do an extra query for the `UserProfile` each time you need those fields.

[[ MOVE THIS TO A BLOG POST ]]

If you plan on subclassing `User` into multiple models (say, `CoordinatorUser` and `VolunteerUser`) then this packages is probably not
your best option. You might use a [pattern](http://schinckel.net/2011/10/09/why-customuser-subclasses-are-not-such-a-good-idea/) like Matthew Schickel suggests.

There have been many arguments against subclassing using ([here](http://www.b-list.org/weblog/2007/feb/20/about-model-subclassing/)), but I haven't found
any of them compelling enough to make up for the coding efficiency gains that subclassing offers (see benefits list above). The User subclassing approach offered
in this app is a reusable implementation of the subclassing approach that has been documenting in many blog posts ([here](http://scottbarnham.com/blog/2008/08/21/extending-the-django-user-model-with-inheritance/))

If you plan on utilizing the subclassing aspects of this application, it is best to use them from the beginning so you don't have a mix of User and SubclassedUser entries in the database.


# Roadmap

Development TODO list:

  * Invitation clean up and tests

Features to add:

  * Admin login form should handle email-only authentication
  * Email confirmation on registration
  * Implement `LOGOUT_REDIRECT_URL`
  * Better built in password rules. Options for extending the password rules.
  * Refactor token URL generation to `utils.py`
  * Change email form and email confirmation page
  * Ability to add, link, and confirm multiple email addresses to the same account (separate app)

Improvements to documentation:

  * Write sphinx documentation
  * Step by step of password reset process and how it works
  * List all template paths that the default templates will look for
  * Change PACKAGEPATHHERE in the quickstart guide once this is up on github
  * Add link to github issue queue in the "contributing" section
  * Add link to blog post about subclassing the user


# Contributing
Please fork this repo and send pull requests. Submit issues/questions/suggestions in the issue queue.


# Author
Built at [Concentric Sky](http://www.concentricsky.com/) by [Jeremy Blanchard](http://github.com/auzigog/).

This project is licensed under the [Apache License, Version 2.0](http://www.apache.org/licenses/LICENSE-2.0). Copyright 2012 Concentric Sky, Inc.



