#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

import django
from django.conf import settings
from django.core.management import (
                                    execute_from_command_line,
                                    call_command
                                    )


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djhello.settings')
    django.setup()

    settings.debug = False

    #execute_from_command_line("runserver --noreload 8000".split())
    call_command("runserver", noreload=False, addrport="0.0.0.0:8000")


if __name__ == '__main__':
    main()
