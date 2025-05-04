var _a;
var roomName = "{{ room_name }}";
var chatSocket = new WebSocket(
//criação de um WebSocket para se conectar ao servidor.
'ws://' + window.location.host + '/ws/chat/' + roomName + '/'
//concatenando a URL do servidor (window.location.host) com o caminho (/ws/chat/{room_name})
);
chatSocket.onmessage = function (e) {
    //onmessage -> evento que é disparado quando o WebSocket recebe uma mensagem do servidor.
    //e : MessageEvent -> o parâmetro "e" contém as informações sobre a mensagem recebida pela propriedade data, vinda do MessageEvent.
    var data = JSON.parse(e.data);
    //e.data -> string JSON que será convertida em um objeto javascript através do JSON.parse(e.data).
    var chatMain = document.querySelector(".chatMain");
    //chatMain -> busca o elemento ".chatMain", onde as mensagens serão exibidas.
    if (chatMain) {
        //como o querySelector pode retornar null, é preciso verificar se "chatMain" é válido.
        var msgDiv = document.createElement("div");
        msgDiv.textContent = data.message;
        //adiciona o conteúdo do "data.message" em forma de texto na Div criada.
        chatMain.appendChild(msgDiv);
        //adiciona a div como "filha" do chatMain.
        chatMain.scrollTop = chatMain.scrollHeight;
        //faz com que o chat role para o final quando uma nova mensagem for recebida.
    }
};
chatSocket.onclose = function (e) {
    //"e" recebe o event de fechamento do WebSocket
    console.error("WebSocket fechado inesperadamente");
    //caso ocorra esse fechamento, o console irá mostrar essa mensagem de erro.
};
(_a = document.querySelector(".sendButton")) === null || _a === void 0 ? void 0 : _a.addEventListener("click", function () {
    //busca do botão ".sendButton". A interrogação garante a checagem para ver se o botão foi encontrado.
    var input = document.querySelector(".inputConfig");
    if (input) {
        var message = input.value;
        //guarda na variável message o que foi escrito no input.
        chatSocket.send(JSON.stringify({ "message": message }));
        //converte o conteúdo de message para uma string JSON.
        input.value = "";
    }
});
