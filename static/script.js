var socket = io();
var username = "Loading..."; // Default value

// Get username from the backend
fetch('/get_username')
    .then(response => response.json())
    .then(data => {
        username = data.username;
        document.getElementById("userDisplay").innerText = username;
    });

// Listen for messages
socket.on('message', function(data) {
    let messageBox = document.createElement('div');
    messageBox.innerHTML = `<b>${data.username}</b>: ${data.message} <small>(${data.timestamp})</small>`;
    document.getElementById('chat').appendChild(messageBox);
});

// Send message function
function sendMessage() {
    let messageInput = document.getElementById('messageInput');
    let message = messageInput.value;
    if (message.trim() !== "") {
        socket.send({'message': message});
        messageInput.value = "";
    }
}
