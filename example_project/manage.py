#!/usr/bin/env python
import os
import sys


# Insert the app that this is an example project for
PROJ_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJ_DIR not in sys.path:
    sys.path.insert(0, PROJ_DIR)

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "example_project.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
