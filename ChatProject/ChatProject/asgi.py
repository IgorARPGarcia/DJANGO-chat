"""
ASGI config for ChatProject project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from chatApp import routing 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ChatProject.settings')

application = ProtocolTypeRouter({
    #ProtocolTypeRouter -> responsável por direcionar protocolos (HTTP, WebSocket, etc.) para o lugar apropriado.
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        #AuthMiddlewareStack -> camada de segurança que gerencia a autenticação de usuários para as conexões WebSocket.
        URLRouter(
            routing.websocket_urlpatterns
            #URLRouter(rounting.) -> pega as rotas defindas em websocket_urlpatterns, no arquivo routings.py
        )
    ),
})
