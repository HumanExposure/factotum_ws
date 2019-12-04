#!/usr/bin/env python
import sys

from config.environment import env


def main():

    try:
        from django.core.management import execute_from_command_line
    except ImportError:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        )
    from django.core.management.commands.runserver import Command as runserver

    runserver.default_port = env.FACTOTUM_WS_PORT
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
