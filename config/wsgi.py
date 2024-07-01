"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')


def startup():
    """
    This method initialize our connection and services
    """

    from apps.desing_patterns.creational_patterns.singleton.openai_singleton import OpenAISingleton
    print(OpenAISingleton())


startup()
application = get_wsgi_application()
