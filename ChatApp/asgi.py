import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application

# Set the default settings module for the 'DJANGO_SETTINGS_MODULE' environment variable
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ChatApp.settings')

# Ensure Django is set up before importing any models or middleware
django.setup()

# Import your routing configuration and custom middleware after Django setup
from Messenger_API.middleware import JWTAuthMiddleware
from Messenger_API import routing

# ASGI application
application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # HTTP protocol handling
    "websocket": JWTAuthMiddleware(  # WebSocket protocol handling
        AuthMiddlewareStack(
            URLRouter(
                routing.websocket_urlpatterns
            )
        )
    ),
})
