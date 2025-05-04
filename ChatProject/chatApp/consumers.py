import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer

class ChatConsumer(AsyncJsonWebsocketConsumer):
    #ChatConsumer -> consumer para tratar a comunicação via WebSocket.
    #AsyncJsonWebSocketConsumer -> class base do Django usada para lidar com WebSockets.
    
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        #self.scope -> age como o request das views, guardando informações sobre a conexão.
        #scope['url_route']['kwargs'] -> recebe os parâmetros da url WebSocket (exemplo: room_name).
        #self.room_name -> nome da sala extraído da URL de routing.py.
        self.room_group_name = f'chat_{self.room_name}'
        #self.room_group_name -> criação do nome do grupo no Redis para identificar cada sala.

        await self.channel_layer.group_add(
            #await -> é usado para esperar que uma função *assíncrona* termine antes da execução do código prosseguir.
            #channel_layer -> interface que conecta os consumers entre si (via Redis).
            #group_add(grupo, canal) -> Adiciona o consumer ao grupo.
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        #aceita a conexão WebSocket (sem isso, a conexão é rejeitada).

    async def disconnect(self, close_code):
        #group_discard -> remove esse WebSocket do grupo, impedindo que ele continue recebendo mensagens
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        #text_data -> é a mensagem recebida do WebSocket (em formato de texto JSON).
        text_data_json = json.loads(text_data)
        #json.loads() -> converte a string JSON em um dicionário Python.
        message = text_data_json['message']
        #message -> pega o conteúdo real da mensagem enviada pelo usuário.

        await self.channel_layer.group_send(
            #group_send() -> envia uma mensagem para todos do grupo (sala).
            self.room_group_name,
            {
                'type': 'chat_message',
                #'type': 'chat_message' -> define qual função será chamada quando o grupo receber a mensagem.
                #nesse caso, irá chamar o método chat_message(self, event).
                'message': message,
                'sender_channel': self.channel_name  # <- identifica quem enviou
            }
        )

    async def chat_message(self, event):
        message = event['message']
        sender_channel = event['sender_channel']
        #message = event['message'] -> mensagem enviada por outro usuário.

        is_sender = self.channel_name == sender_channel
        # compara se quem está recebendo é o mesmo que enviou

        await self.send(text_data=json.dumps({
            #self.send() -> envia a mensagem para este WebSocket específico.
            'message': message,
            'sentByUser': is_sender
            #json.dumps() -> converte de dicionário para string JSON.
        }))

        
        