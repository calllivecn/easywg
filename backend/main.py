#!/usr/bin/env python3
"""Django's command-line utility for administrative tasks."""
import os
import sys
from threading import Thread, Lock

import django
from django.conf import settings
from django.core.management import (
                                    execute_from_command_line,
                                    call_command
                                    )


def backtask():
    th = Thread(target=startserver, daemon=True)
    th.start()

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'easywg.settings')

    settings.debug = False

    django.setup()

    #execute_from_command_line("runserver --noreload 8000".split())

    print("makemigrations")
    call_command("makemigrations")

    print("migrate")
    call_command("migrate")

    print("startwg to back task...")
    backtask()

    print("runserver")
    call_command("runserver", noreload=False, addrport="0.0.0.0:8000")
    print("runserver 之后")

if __name__ == '__main__':
    main()
