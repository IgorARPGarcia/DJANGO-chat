var a;
//variavel para armazenar temporariamente o sendButton.
const roomName = document.body.dataset.roomName;
//pega o nome da sala onde o usuário está através do atributo data-room-name no body do html.

var chatSocket = new WebSocket(
    //cria a conexão WebSocket com o servidor, construindo a URL com o nome da sala atual.
    'ws://' + window.location.host + '/ws/chat/' + roomName + '/'
);

//função para adicionar mensagem no chat
function addMessageToChat(message, sentByUser) {
    const chatMain = document.querySelector(".chatMain");
    //procura o elemento html onde as mensagens serão exibidas.
    if (chatMain) {
        //verifica se ele existe.
        const messageDiv = document.createElement('div');
        //cria uma nova div para a mensagem. 
        messageDiv.classList.add('message');
        //adiciona a classe message a div.
        messageDiv.classList.add(sentByUser ? 'sent' : 'received');
        //adiciona uma classe condicional. "sent" se foi enviada e "received" se foi recebida.
        messageDiv.textContent = message;
        //define o texto da mensagem.

        chatMain.appendChild(messageDiv);
        //adiciona a mensagem ao chat.

        chatMain.scrollTop = chatMain.scrollHeight;
        //faz scroll automático para o final do chat.
    }
}

// Configuração do chat
a = document.querySelector(".sendButton").addEventListener("click", function () {
    var input = document.querySelector(".inputConfig");
    //coloca na variavel input o valor digitado no ".inputConfig"
    if (input) {
        //verifica se o input existe.
        var message = input.value;
        //armazena o valor do input na variavel message.
        chatSocket.send(JSON.stringify({ "type": "chat", "message": message, "sentByUser": true }));
        //converte a mensagem para uma string JSON e envia para o WebSocket.
        addMessageToChat(message, true);
        //Mostra a mensagem no chat.
        input.value = "";
        //limpa o campo do input.
    }
});

const inputField = document.querySelector('.inputConfig');
//Mesma função utilizada anteriormente mas para o botão "Enter" do teclado.
if (inputField) {
    inputField.focus();
    inputField.onkeyup = function(e) {
        if (e.key === 'Enter') {
            const message = inputField.value;
            chatSocket.send(JSON.stringify({ "type": "chat", 'message': message, 'sentByUser': true }));
            addMessageToChat(message, true);
            inputField.value = '';
        }
    };
}

//variáveis do jogo da velha.
let currentPlayer = null;
//variavel que define o jogador atual.
let isMyTurn = false;
//variavel que define se é minha vez ou não;
let gameActive = false;
//se o jogo estava ativo ou não.

//simbolos dos jogadores.
const PLAYER_SYMBOLS = {
    img1: {
        img: '/static/chat/images/icons8-reciclagem-64.png',
        alt: 'Reciclagem'
    },
    img2: {
        img: '/static/chat/images/bottle.png',
        alt: 'Garrafa'
    }
    //define os simbolos de cada jogador (imagens).
};

//função para limpar o tabuleiro
function limparTabuleiro() {
    document.querySelectorAll('.celula').forEach(cell => {
        cell.classList.remove('played');
        cell.innerHTML = '';
        //remove a classe "played" e remove as imagens.
    });
}

//função para voltar ao chat
function voltarAoChat() {
    document.querySelector(".chatDiv").style.display = "block";
    //traz o chat novamente.
    document.querySelector("#jogoMain").style.display = "none";
    //esconde o jogo.
    gameActive = false;
}

//função para iniciar o jogo.
function abrirJogo() {
    limparTabuleiro();
    //limpa o tabuleiro antes de iniciar o jogo.
    document.querySelector(".chatDiv").style.display = "none";
    //esconde o chat.
    document.querySelector("#jogoMain").style.display = "block";
    //mostra o jogo.
    gameActive = true;
    
    //só mostra o símbolo se já estiver atribuído
    if (currentPlayer) {
        const symbolInfo = PLAYER_SYMBOLS[currentPlayer];
        alert(`Você é o ${symbolInfo.alt}! ${currentPlayer === 'img1' ? 'Você começa!' : 'Aguarde sua vez...'}`);
        //mostra para o jogador qual o seu simbolo e se é sua vez.
        isMyTurn = currentPlayer === 'img1';
    }
    
    chatSocket.send(JSON.stringify({ "type": "game_start" }));
    //manda para o servidor que o jogo começou.
}

//botão para voltar ao chat
const backButton = document.createElement('button');
backButton.textContent = 'Voltar ao Chat';
backButton.classList.add('back-button');
backButton.onclick = voltarAoChat;
backButton.style.backgroundColor = ("#3e7b45");
backButton.style.color = ("#ffffff");
backButton.style.border = ("none");
document.querySelector("#jogoMain").appendChild(backButton);

//renderiza jogada no tabuleiro
function renderJogada(index, playerType) {
    //index -> representa a posição clicada (de 0 a 8).
    //playerType -> string que representa o jogador (img1 ou img2).
    
    const cell = document.querySelector(`.celula[data-index="${index}"]`);
    //passa um atributo data-index a div clicada, com um valor igual ao do index.

    if (cell && !cell.classList.contains('played') && gameActive) {
        //verifica se a celula existe e se ja foi "jogada" (contém a classe played ou não)
        cell.classList.add('played');
        //adiciona a classe played à célula para marcar e impedir que outra pessoa jogue na mesma.
        const img = document.createElement('img');
        //cria um novo elemento (img) e coloca a imagem escolhida lá.
        img.src = PLAYER_SYMBOLS[playerType].img;
        img.alt = PLAYER_SYMBOLS[playerType].alt;
        cell.appendChild(img);
    }
}

//eventos das células
document.querySelectorAll('.celula').forEach(cell => {
    cell.addEventListener('click', () => {
        //adiciona função de click a cada célula.
        
        const index = cell.dataset.index;
        //pega o núumero da célula.

        if (!cell.classList.contains('played') && isMyTurn && currentPlayer && gameActive) {
            //caso a célula escolhida não contenha a classe "played", caso seja sua vez, caso você seja o player atual e caso o jogo esteja ativo.
            //então a jogada será válida e será enviada como uma string JSON para o socket.
            chatSocket.send(JSON.stringify({
                type: 'jogada',
                index: index,
                player: currentPlayer
            }));
            renderJogada(index, currentPlayer);
            //renderiza a jogada e o jogador atual.
            isMyTurn = false;
            //torna falso o minha vez, permitindo apenas que o outro jogador jogue.
        }
    });
});

//recebimento de mensagens WebSocket
chatSocket.onmessage = function (e) {
    const data = JSON.parse(e.data);
    //e.data -> recebe o conteúdo da mensagem como uma string JSON e converte em um objeto js.

    if (data.type === 'chat') {
        //verifica se a mensagem recebida é do tipo "chat".
        if (data.sentByUser !== true) {
            addMessageToChat(data.message, false);
            //evita que a própra mensagem não duplicada.
        }
    }
    else if (data.type === 'jogada') {
        //verifica se a mensagem é uma jogada no jogo da velha.
        renderJogada(data.index, data.player);
        //renderiza a jogada do jogador correto.
        if (data.player !== currentPlayer) {
            isMyTurn = true;
            //caso a jogada tenha sido do outro jogador, é sua vez.
        }
    }
    else if (data.type === 'assign_symbol') {
        //verifica se a mensagem recebida está atribuido o simbolo ao jogador atual.
        currentPlayer = data.player;
        //atribui o img1 ou img2 ao jogador atual.
        localStorage.setItem(`playerSymbol_${roomName}`, currentPlayer);
        console.log(`Você é o jogador ${currentPlayer}`);
        
        //só mostra o alerta se estivermos no jogo
        if (gameActive) {
            const symbolInfo = PLAYER_SYMBOLS[currentPlayer];
            alert(`Você é o ${symbolInfo.alt}! ${currentPlayer === 'img1' ? 'Você começa!' : 'Aguarde sua vez...'}`);
            isMyTurn = currentPlayer === 'img1';
            //define que é sua vez se você é o jogador 1 (que sempre começa).
        }
    }
    else if (data.type === 'game_start') {
        // Atualiza o estado do jogo
        gameActive = true;
    }
    else if (data.type === 'game_result') {
        gameActive = false;
        
        if (data.result === 'win') {
            const winnerSymbol = PLAYER_SYMBOLS[data.winner];
            const victoryMessage = data.winner === currentPlayer ? 
                'Você venceu!' : 
                `${winnerSymbol.alt} venceu!`;
            alert(victoryMessage);
        } else if (data.result === 'draw') {
            alert('Jogo empatado!');
        }
        
        setTimeout(voltarAoChat, 3000);
    }
    else if (data.type === 'player_disconnected') {
        alert(data.message);
        voltarAoChat();
    }
};

chatSocket.onclose = function (e) {
    console.error("WebSocket fechado inesperadamente");
    alert("Conexão perdida. Recarregue a página para tentar novamente.");
};

// Inicialização
chatSocket.onopen = function () {
    currentPlayer = localStorage.getItem(`playerSymbol_${roomName}`);
    if (!currentPlayer) {
        console.log("Aguardando servidor atribuir símbolo...");
    } else {
        console.log(`Você é o jogador ${currentPlayer}`);
    }
};