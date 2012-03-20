
def get_user_model():
    from django.conf import settings
    # Grab the user model path
    try:
        model_path = getattr(settings, 'CUSTOM_USER_MODEL', None)
    except AttributeError:
        raise Exception(u"Cannot find your specified CUSTOM_USER_MODEL. Are CustomUser and your CustomUser-subclass app both in your INSTALLED_APPS?")
    if model_path is None:
        raise Exception(u"You must define a CUSTOM_USER_MODEL in your settings")

    parts = model_path.split('.')
    model_name = parts.pop()
    parts.append('models')
    module = __import__('.'.join(parts))
    model_class = getattr(module.models, model_name)
    return model_class

SubclassedUser = get_user_model()