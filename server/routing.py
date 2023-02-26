from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from channels.routing import ProtocolTypeRouter, URLRouter
import request.routing
from django.core.asgi import get_asgi_application
from request.middlewares import TokenAuthMiddleWare
django_asgi_app = get_asgi_application()
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    'websocket': TokenAuthMiddleWare(
                AllowedHostsOriginValidator(
                    URLRouter(
                        request.routing.websocket_urlpatterns
                    )
    )),
})