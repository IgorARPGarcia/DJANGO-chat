from django.urls import re_path
from chatApp import consumers
#consumer é uma classe que lida com conexões, ela recebe, envia e gerencia mensagens.

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
    #re_path -> é uma função para mapear a URL do WebSocket.
    #nesse caso, a url vai ter a forma ws/chat/(?P<room_name>\w+)/$, onde <room_name> é o nome da sala do chat.
    #consumers.ChatConsumer.as_asgi() -> função para dizer que o django deve usar o ChatConsumer.
    #as_asgi() -> função para converter a classe em questão para um objeto compativel com asgi.
]

