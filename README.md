Extension to the django authentication/user system.

ADD TO README:

  * Benefits of subclassing: easier to write queries on our end.
  * Subclassing: always does an inner join on your table and the auth.user table.

# Features

  * Adds password rules to field


# Settings
Must specify `SECRET_KEY` in your settings for the invitation process to be secure.


# Admin
By default, we remove the admin screens for Auth User and place in an auth screen for you authentication

If you want to re-add the the django contrib user, you can do that by re-registering django.contrib.auth.User

If you want fine-grained control over the admin you can subclass the CustomUser module:

   from custom_user.admin import UserAdmin

   class MyUserAdmin(UserAdmin):
       # Your code here
       pass

   admin.site.register(MyUser, MyUserAdmin)