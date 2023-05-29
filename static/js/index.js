const chatLog = document.getElementById('chat-log');
const chatForm = document.getElementById('chat-form');
const chatMessageInput = document.getElementById('chat-message-input');
const user_name = JSON.parse(document.getElementById('user_name').textContent);

let loc = window.location
let wsStart = 'ws://'

if(loc.protocol === 'https') {
    wsStart = 'wss://'
}

let endpoint = wsStart + loc.host + loc.pathname

var socket = new WebSocket(endpoint)

socket.onopen = async function(e){
    console.log('open', e)
}

socket.onmessage = function(event) {
    console.log(event);
    const data = JSON.parse(event.data);
    const message = data.message;
    const username = data.username;
    const messageElement = document.createElement('p');
    messageElement.innerText = `${username}: ${message}`;
    chatLog.appendChild(messageElement);
};

chatForm.addEventListener('submit', function(event) {
    event.preventDefault();
    const message = chatMessageInput.value;
    socket.send(JSON.stringify({
        'message': message,
        'username': user_name
    }));
    chatMessageInput.value = '';
});