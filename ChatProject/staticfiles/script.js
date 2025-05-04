var _a;
const roomName = document.body.dataset.roomName;
console.log(roomName);

var chatSocket = new WebSocket(
// criação de um WebSocket para se conectar ao servidor.
'ws://' + window.location.host + '/ws/chat/' + roomName + '/'
// concatenando a URL do servidor (window.location.host) com o caminho (/ws/chat/{room_name})
);

// função para adicionar a mensagem no chat com estilo (direita/esquerda)
function addMessageToChat(message, sentByUser) {
    const chatMain = document.querySelector(".chatMain");
    //chatMain -> busca o elemento ".chatMain", onde as mensagens serão exibidas.
    if (chatMain) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message');
        messageDiv.classList.add(sentByUser ? 'sent' : 'received');
        messageDiv.textContent = message;

        chatMain.appendChild(messageDiv);
        chatMain.scrollTop = chatMain.scrollHeight;
        //faz com que o chat role para o final quando uma nova mensagem for exibida.
    }
}

chatSocket.onmessage = function (e) {
    // onmessage -> evento que é disparado quando o WebSocket recebe uma mensagem do servidor.
    // e : MessageEvent -> o parâmetro "e" contém as informações sobre a mensagem recebida pela propriedade data, vinda do MessageEvent.
    const data = JSON.parse(e.data);
    // e.data -> string JSON que será convertida em um objeto javascript através do JSON.parse(e.data).
    addMessageToChat(data.message, false); // false porque é mensagem recebida
};

chatSocket.onclose = function (e) {
    //"e" recebe o event de fechamento do WebSocket
    console.error("WebSocket fechado inesperadamente");
    //caso ocorra esse fechamento, o console irá mostrar essa mensagem de erro.
};

(_a = document.querySelector(".sendButton")) === null || _a === void 0 ? void 0 : _a.addEventListener("click", function () {
    var input = document.querySelector(".inputConfig");
    if (input) {
        var message = input.value;
        chatSocket.send(JSON.stringify({ "message": message, "sentByUser": true }));
        addMessageToChat(message, true);  // Enviado pelo usuário
        input.value = "";
    }
});

const inputField = document.querySelector('.inputConfig');
if (inputField) {
    inputField.focus();
    inputField.onkeyup = function(e) {
        if (e.key === 'Enter') {
            const message = inputField.value;
            chatSocket.send(JSON.stringify({ 'message': message, 'sentByUser': true }));
            addMessageToChat(message, true);  // Enviado pelo usuário
            inputField.value = '';
        }
    };
}


chatSocket.onmessage = function (e) {
    const data = JSON.parse(e.data);

    // Verifica se a mensagem foi enviada por outro usuário (não duplicada)
    if (data.sentByUser !== true) { 
        addMessageToChat(data.message, false); // Se não foi enviada pelo próprio usuário, adiciona
    }
};


