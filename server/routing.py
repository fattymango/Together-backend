
from channels.security.websocket import AllowedHostsOriginValidator
from channels.routing import ProtocolTypeRouter, URLRouter
import request.routing
import user.routing
from django.core.asgi import get_asgi_application
from request.middlewares import TokenAuthMiddleWare

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    'websocket': TokenAuthMiddleWare(
                AllowedHostsOriginValidator(
                    URLRouter(
                        request.routing.websocket_urlpatterns+
                        user.routing.websocket_urlpatterns
                    )
    ))})