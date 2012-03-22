Extension to the django authentication/user system.

ADD TO DOCS:

  * Benefits of subclassing: easier to write queries on our end.
  * Subclassing: always does an inner join on your table and the auth.user table.
  * Version 0.1.0 -- In development
  * Fix pip package path
  * Many pages pass error messages around using the messages framework. You should have it enabled on all custom_user templates.
  * Info about auto login after the password reset completes
  * Step by step of password reset process and how it works
  * Don't create users with createsuperuser or django.contrib.auth.models.User.create_user() because there won't be a proper entry in the subclassed user table for them
  * On EmailCustomUser you can set `validate_email_uniqeness` to false if you're concerned about the extra database query for each call to clean()

# Features

  * Email-based authentication. Hides username
  * Adds password rules to field


# Usage
Throughout this app, any class beginning with `Email` indicates that it is for use with email-only authentication systems.
In all cases, there should be a matching class without `Email` at the beginning of the class name that is for use with username-focused authentication systems.


## Quickstart

  * `pip install PACKAGEPATHHERE`
  * Add `custom_user` near the top of your `INSTALLED_APPS` setting
  * Somewhere in your own `myapp.models.py`, define one of the two following code blocks:

```python
# Assume this is in myapp.models
from custom_user import EmailCustomUser, EmailUserManager

class User(EmailCustomUser):
    objects = EmailUserManager()
```

  * In your're `settings.py` add these lines:

```python
# Change myapp to the name of the app where you extend EmailCustom
CUSTOM_USER_MODEL = 'myapp.User'
AUTHENTICATION_BACKENDS = [
    'custom_user.backends.EmailBackend',
]
```


  *



# Settings
Must specify `SECRET_KEY` in your settings for the invitation process to be secure.


# Admin
By default, we remove the admin screens for Auth User and place in an auth screen for you authentication

If you want to re-add the the django contrib user, you can do that by re-registering django.contrib.auth.User

If you want fine-grained control over the admin you can subclass the CustomUser module:

```python
from custom_user.admin import UserAdmin

class MyUserAdmin(UserAdmin):
   # Your code here
   pass

admin.site.register(MyUser, MyUserAdmin)
```

# TODO

  * Implement `LOGOUT_REDIRECT_URL`