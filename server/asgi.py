"""
ASGI config for server project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/asgi/
"""

import os

from channels.routing import ProtocolTypeRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()
from channels.security.websocket import AllowedHostsOriginValidator
from channels.routing import ProtocolTypeRouter, URLRouter
import request.routing
import user.routing
import chat.routing
from django.core.asgi import get_asgi_application
from request.middlewares import TokenAuthMiddleWare


application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    'websocket': TokenAuthMiddleWare(
                
                    URLRouter(
                        request.routing.websocket_urlpatterns +
                        user.routing.websocket_urlpatterns +
                        chat.routing.websocket_urlpatterns
                    )
    )})