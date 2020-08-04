#!/usr/bin/env python3
"""Django's command-line utility for administrative tasks.""" 
import os
import sys
import atexit
import shutil
import argparse
from threading import Thread


import django
from django.conf import settings
from django.core.management import (
                                    execute_from_command_line,
                                    call_command
                                    )



from wg.startwg import startserver, stopserver
from libwg.startlock import START_LOCK

def export2staticfile(target):
    if os.path.exists(target):
        print(f"{target} already exists")
        sys.exit(1)
    else:
        shutil.copytree(settings.WEB_ROOT, target)


atexit.register(stopserver)

def backtask():
    with START_LOCK:
        th = Thread(target=startserver, daemon=True)
        th.start()


def parse():

    parse = argparse.ArgumentParser()

    parse.add_argument("--debug", action="store_true", help="debug")
    parse.add_argument("--addr", action="store", default="0.0.0.0", help="listen ip address (default: 0.0.0.0)")
    parse.add_argument("--port", action="store", type=int, default=8000, help="port")
    parse.add_argument("--export-staticfiles", dest="export", action="store", help="export static file to directory.")
    parse.add_argument("--parse", action="store_true", help="print(parse) exit")

    args = parse.parse_args()

    if args.parse:
        print(args)
        sys.exit(0)
    
    if args.export:
        export2staticfile(args.export)
        sys.exit(0)

    return args

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'easywg.settings')
    #settings.configure()

    args = parse()

    if args.debug:
        pass
    else:
        settings.DEBUG = False

    django.setup()

    #execute_from_command_line("runserver --noreload 8000".split())

    print("makemigrations")
    call_command("makemigrations")

    print("migrate")
    call_command("migrate")

    print("startwg to back task...")
    backtask()

    print("runserver")
    call_command("runserver", noreload=False, addrport=f"{args.addr}:{args.port}")
    print("runserver 之后")


if __name__ == '__main__':
    main()
