# Copyright 2012 Concentric Sky, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import get_current_site
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.template import loader
from django.template.context import Context
from django.utils.http import int_to_base36


class TokenTemplateEmail(object):

    def __init__(self, user, email_template_name=None, token_view_name=None, request=None, protocol='http', domain='localhost', subject=None, from_email=None, token_generator=default_token_generator):
        self.user = user
        self.email_template_name = email_template_name
        self.token_view_name = token_view_name
        self.request = request
        self.protocol = protocol
        self.domain = domain
        self.subject = subject
        self.from_email = from_email
        self.token_generator = token_generator
        super(TokenTemplateEmail, self).__init__()

    def get_token_generator(self):
        return self.token_generator

    def get_from_email(self):
        if self.from_email is None:
            return settings.DEFAULT_FROM_EMAIL
        else:
            return self.from_email

    def get_subject(self):
        return self.subject

    def get_email_template_name(self):
        if self.email_template_name is None:
            raise ImproperlyConfigured("No email_template_name. Please provide an email_template_name in the view class.")
        else:
            return self.email_template_name

    def get_complete_token_url_path(self, uidb36, token):
        if self.token_view_name:
            return reverse(self.token_view_name, kwargs={'uidb36': uidb36, 'token': token})
        else:
            raise ImproperlyConfigured("No token_view_name. Please provide a token_view_name in the view class or "
                                        "override get_complete_token_url_path().")

    def get_domain(self):
        """
        Override this function to have control what domain the token_url in the context_data contains
        """
        return self.domain

    def get_site_name(self):
        """
        Used in the default email template to provide a more verbose name for your site. Defaults to the domain.
        """
        return self.get_domain()

    def get_context_data(self):
        context_data = {
            'email': self.user.email,
            'domain': self.get_domain(),
            'site_name': self.get_site_name(),
            'uid': int_to_base36(self.user.id),
            'user': self.user,
            'token': self.get_token_generator().make_token(self.user),
            'protocol': self.protocol,
        }
        context_data['token_url_path'] = self.get_complete_token_url_path(uidb36=context_data['uid'], token=context_data['token'])
        context_data['token_url'] = '%s://%s%s' % (context_data['protocol'], context_data['domain'], context_data['token_url_path'])
        return context_data

    def send_email(self):
        """
        This plus get_context_data() is effectively the same email sending process as auth.forms.PasswordResetForm.save()
        """
        t = loader.get_template(self.get_email_template_name())
        context_data = self.get_context_data()
        return send_mail(self.get_subject(), t.render(Context(context_data)), self.get_from_email(), [context_data['email']])
