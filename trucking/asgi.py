"""
ASGI config for trucking project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

from trucking.settings  import base # or dev

if base.DEBUG:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trucking.settings.dev')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trucking.settings.prod')


application = get_asgi_application()
