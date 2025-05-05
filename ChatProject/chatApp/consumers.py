import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer

class ChatConsumer(AsyncJsonWebsocketConsumer):
    rooms = {}  
    # Dicionário de classe para armazenar as salas.

    async def connect(self):
        #método assincrono chamado quando há conexão com o WebSocket.
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        #pega o nome da sala da URL.
        self.room_group_name = f'chat_{self.room_name}'
        #define o nome do grupo para fazer a comunicação interna com o django.

        #inicializa a sala se não existir.
        if self.room_name not in self.rooms:
            self.rooms[self.room_name] = {
                'players': {},
                'symbols': ['img1', 'img2'],  #usando img1 e img2 para as imagens.
                'game_started': False,
                'current_turn': 'img1',  #img1 começa.
                'board': [None] * 9,  #tabuleiro 3x3.
                'moves_count': 0
            }

        room = self.rooms[self.room_name]

        #verifica se há espaço na sala (máximo 2 jogadores).
        if len(room['players']) >= 2:
            await self.close()
            #rejeita a conexão se houver mais de 2 jogadores.
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        #atribui um símbolo ao jogador
        player_type = room['symbols'].pop(0) if room['symbols'] else None
        #retira o próximo simbolo da lista para ninguem pegar o mesmo.
        room['players'][self.channel_name] = {
            'player_type': player_type,
            'ready': False
        }

        #envia o tipo de jogador para o cliente.
        await self.send(text_data=json.dumps({
            'type': 'assign_symbol',
            'player': player_type
        }))

        #se dois jogadores estiverem conectados, notifica ambos.
        if len(room['players']) == 2:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'game_ready',
                    'message': 'Dois jogadores conectados! O jogo pode começar.'
                }
            )

    async def disconnect(self, close_code):
        if self.room_name in self.rooms:
            room = self.rooms[self.room_name]
            if self.channel_name in room['players']:
                player_info = room['players'][self.channel_name]
                #devolve o símbolo ao pool se o jogador sair
                if player_info['player_type']:
                    room['symbols'].insert(0, player_info['player_type'])
                del room['players'][self.channel_name]

                #notifica o outro jogador sobre a desconexão
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': 'Um jogador saiu da sala. Jogo encerrado.',
                        'sender_channel': self.channel_name
                    }
                )

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        #converte a mensagem de texto para string JSON.
        message_type = text_data_json.get('type', 'chat')
        #pega o tipo da mensagem (tipo: "chat").

        if message_type == 'chat':
            message = text_data_json['message']
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'sender_channel': self.channel_name
                }
            ) #envia a mensagem a todos do chat.

        elif message_type == 'jogada':
            room = self.rooms[self.room_name]
            player_info = room['players'][self.channel_name]
            index = int(text_data_json['index'])

            #verifica se é a vez do jogador e se a célula está vazia.
            if (room['current_turn'] == player_info['player_type'] and 
                room['board'][index] is None and 
                room['game_started']):
                #só permite a jogada se for a vez do jogador e se a célula estiver vazia.

                #atualiza o tabuleiro.
                room['board'][index] = player_info['player_type']
                room['moves_count'] += 1

                #envia a jogada para todos.
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'jogada_message',
                        'index': index,
                        'player': player_info['player_type']
                    }
                )

                #verifica se há vencedor.
                winner = self.check_winner(room['board'])
                if winner:
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'game_result',
                            'result': 'win',
                            'winner': winner,
                            'message': f'Jogador {winner} venceu! Voltando ao chat...'
                        }
                    )
                    await self.reset_game()
                    
                elif room['moves_count'] >= 9:  #empate caso todas as células sejam preenchidas.
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'game_result',
                            'result': 'draw',
                            'message': 'Jogo empatado! Voltando ao chat...'
                        }
                    )
                    await self.reset_game()
                else:
                    #alterna o turno caso o jogo não tenha acabado ainda.
                    room['current_turn'] = 'img2' if player_info['player_type'] == 'img1' else 'img1'

        elif message_type == 'game_start':
            room = self.rooms[self.room_name]
            if len(room['players']) == 2 and not room['game_started']:
                room['game_started'] = True
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'game_start_message',
                        'status': 'started'
                    }
                ) #começa o jogo oficialmente caso tenha 2 jogadores.

        elif message_type == 'back_to_chat':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'back_to_chat_message'
                }
            ) #comando para retornar a tela do chat.

    def check_winner(self, board):
        #combinações vencedoras (linhas, colunas, diagonais)
        win_conditions = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # linhas
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # colunas
            [0, 4, 8], [2, 4, 6]              # diagonais
        ]

        for condition in win_conditions:
            if (board[condition[0]] is not None and
                board[condition[0]] == board[condition[1]] == board[condition[2]]):
                return board[condition[0]]  #retorna 'img1' ou 'img2'.
        return None
    #se ninguem venceu, retorna none.

    async def reset_game(self):
        #reseta o estado do jogo para uma nova partida.
        room = self.rooms[self.room_name]
        room['board'] = [None] * 9
        room['moves_count'] = 0
        room['game_started'] = False
        room['current_turn'] = 'img1'

    #handlers de mensagens.
    async def chat_message(self, event):
        #envia a mensagem de chat ao cliente.
        message = event['message']
        sender_channel = event['sender_channel']
        is_sender = self.channel_name == sender_channel

        await self.send(text_data=json.dumps({
            'type': 'chat',
            'message': message,
            'sentByUser': is_sender
        }))

    async def jogada_message(self, event):
        #envia a jogada feita.
        await self.send(text_data=json.dumps({
            'type': 'jogada',
            'index': event['index'],
            'player': event['player']
        }))

    async def game_ready(self, event):
        #informa que jogo pode começar.
        await self.send(text_data=json.dumps({
            'type': 'game_ready',
            'message': event['message']
        }))

    async def game_start_message(self, event):
        #informa que o jogo começou.
        await self.send(text_data=json.dumps({
            'type': 'game_start',
            'status': event['status']
        }))

    async def game_result(self, event):
        #informa vitória ou empate.
        await self.send(text_data=json.dumps({
            'type': 'game_result',
            'result': event['result'],
            'winner': event.get('winner'),
            'message': event['message']
        }))

    async def back_to_chat_message(self, event):
        #informa para voltar ao chat.
        await self.send(text_data=json.dumps({
            'type': 'back_to_chat'
        })) 