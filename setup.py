#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

from setuptools import setup
import re
import os
import sys

name = 'django-extended-auth'
package = ''
description = 'Extension to the django authentication/user system.'
url = 'http://github.com/concentricsky/django-custom-user/' # TODO: set real URL
author = 'Concentric Sky'
author_email = 'django@concentricsky.com'
license = 'Apache 2.0'
install_requires = []
classifiers = [
    'Operating System :: MacOS :: MacOS X',
    'Operating System :: Microsoft :: Windows',
    'Operating System :: POSIX :: Linux',
    'Programming Language :: Python',
    'Framework :: Django',
    'License :: OSI Approved :: Apache Software License',
    'Topic :: Software Development :: Libraries',
]

try:
    longdesc = open('README.md').read()
except Exception:
    longdesc = ('Breakdown is a lightweight python webserver that parses '
                'jinja2 templates. It\'s intended to be used by designers '
                'in rapid prototyping.')

def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    import extended_auth
    return '.'.join(extended_auth.__version__)


def get_packages(package):
    """
    Return root package and all sub-packages.
    """
    return [dirpath
            for dirpath, dirnames, filenames in os.walk(package)
            if os.path.exists(os.path.join(dirpath, '__init__.py'))]


def get_package_data(package):
    """
    Return all files under the root package, that are not in a
    package themselves.
    """
    walk = [(dirpath.replace(package + os.sep, '', 1), filenames)
            for dirpath, dirnames, filenames in os.walk(package)
            if not os.path.exists(os.path.join(dirpath, '__init__.py'))]

    filepaths = []
    for base, filenames in walk:
        filepaths.extend([os.path.join(base, filename)
                          for filename in filenames])
    return {package: filepaths}


if sys.argv[-1] == 'publish':
    os.system("python setup.py sdist upload")
    args = {'version': get_version(name)}
    print "You probably want to also tag the version now:"
    print "  git tag -a %(version)s -m 'version %(version)s'" % args
    print "  git push --tags"
    sys.exit()


setup(
    name=name,
    version=get_version(package),
    url=url,
    license=license,
    description=description,
    author=author,
    author_email = author_email,
    packages=get_packages(package),
    package_data=get_package_data(package),
    install_requires=install_requires,
    classifiers=classifiers,
    longdesc = longdesc,
)