"""
WSGI config for trucking project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

from trucking.settings  import base # or dev

if base.DEBUG:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trucking.settings.dev')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trucking.settings.prod')

application = get_wsgi_application()
