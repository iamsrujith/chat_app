const userElement = document.getElementById('user');
const userData = JSON.parse(userElement.textContent);
let loc = window.location;
let wsStart = 'ws://';
const connectDiv = document.querySelector('.connect');
const pElement = connectDiv.querySelector('p');
const h1Element = connectDiv.querySelector('h1');

if (loc.protocol === 'https:') {
  wsStart = 'wss://';
}

let endpoint = wsStart + loc.host + "/matching/";

var socket = new WebSocket(endpoint);

socket.onopen = async function(e) {
  console.log('open', e);
};

socket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    if ('redirect' in data) {
        const redirect = data.redirect;
        const userIds = redirect.match(/\d+/g).map(Number);
        if (userIds.includes(userData)) {
            window.location.href = redirect;
        }
        socket.send(JSON.stringify({
            'redirect': redirect,
        }));
    } else if ('error' in data) {
      const error = data.error;
      pElement.textContent = error;
      h1Element.textContent = "oops..";
    }
};