"""WSGI config for the CineQuest project.

This module exposes the WSGI callable used by production servers
such as Gunicorn or uWSGI.
"""

import os
from django.core.wsgi import get_wsgi_application

# Ensure Django knows which settings module to load at process startup.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cinequest.settings")

# WSGI server imports this callable to serve the Django application.
application = get_wsgi_application()
