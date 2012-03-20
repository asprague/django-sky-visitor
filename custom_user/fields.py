from django import forms
from django.forms import widgets
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User as AuthUser


class Html5EmailInput(widgets.Input):
    input_type = 'email'

class UniqueRequiredEmailField(forms.EmailField):
    nonunique_error = _("This email address is already in use. Please enter a different email address.")
    required = True

    def __init__(self, *args, **kwargs):
        if not 'label' in kwargs:
            # It's not standard practice to provide a default label, but it seemed appropriate to keep this in one place in the code
            kwargs['label'] = _("Email")
        if not 'widget' in kwargs:
            kwargs['widget'] = Html5EmailInput()
        super(UniqueRequiredEmailField, self).__init__(*args, **kwargs)

    def clean(self, value):
        value = super(UniqueRequiredEmailField, self).clean(value)
        if AuthUser.objects.filter(email__iexact=value):
            raise forms.ValidationError(self.nonunique_error)
        return value

class PasswordRulesField(forms.CharField):
    DEFAULT_MIN_LENGTH = 8

    # TODO: Add more validators. And move them to validators.py

    def __init__(self, max_length=None, min_length=None, *args, **kwargs):
        if not min_length:
            min_length = self.DEFAULT_MIN_LENGTH
        if not kwargs.get('widget', None):
            kwargs['widget'] = forms.PasswordInput
        super(PasswordRulesField, self).__init__(max_length, min_length, *args, **kwargs)

    def clean(self, value):
        if len(value) < self.min_length:
            raise forms.ValidationError("Password must be at least %d characters long." % self.min_length)
        return super(PasswordRulesField, self).clean(value)
