"""
ASGI config for solar_database project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

#import os

#from django.core.asgi import get_asgi_application

#os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'solar_database.settings')

#application = get_asgi_application()

import os
import django
from channels.routing import get_default_application, ProtocolTypeRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "solar_database.settings")

django.setup()

from django_plotly_dash.routing import application