let user = JSON.parse(document.getElementById('user').innerHTML);
let loc = window.location
let wsStart = 'ws://'

if(loc.protocol === 'https') {
    wsStart = 'wss://'
}

let endpoint = wsStart + loc.host + "/matching/"

var socket = new WebSocket(endpoint)

socket.onopen = async function(e){
    console.log('open', e)
}

socket.onmessage = async function(event) {
    console.log("nobboubbiuvivi")
    console.log(event);
    const data = JSON.parse(event.data);
    const redirect = data.redirect;
    socket.send(JSON.stringify({
        'redirect': redirect,
    }));
    const userIds = redirect.match(/\d+/g).map(Number);
    console.log(userIds)
    if (userIds.includes(user)) {
        window.location.href = redirect;
    }
    await handleChanges(data);
};

async function handleServerChanges(data) {
    const response = data;
    console.log(response)
    }