"""Django's command-line utility for administrative tasks."""

import os
import sys

def main():
    # Point Django CLI commands to this project's settings.
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cinequest.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError("Couldn't import Django.") from exc
    # Delegate command handling (runserver, migrate, createsuperuser).
    execute_from_command_line(sys.argv)

if __name__ == "__main__":
    main()
