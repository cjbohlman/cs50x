


document.addEventListener('DOMContentLoaded', () => {

    // Connect to websocket
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    if (!sessionStorage.getItem("channel")) {
        document.getElementById("add_message").style.visibility = "hidden"; 
        document.getElementById("messages").style.visibility = "hidden"; 
    }

    // When connected, configure buttons
    socket.on('connect', () => {

        document.querySelector('#add_message').onsubmit = () => {
            var user = sessionStorage.getItem('username')
            var message = document.querySelector('#new_message').value
            var channel = sessionStorage.getItem('channel')
            const timestamp = new Date().toUTCString();
            if (!user || user === "") {
                user = "blank"
            }
            if (message === "") {
                return false;
            }
            if (channel === "") {
                return false;
            }

            socket.emit('new message', {'user': user, 'message': message, 'channel': channel, 'timestamp': timestamp});
            return false;
        };

        document.querySelectorAll('#view_channel').forEach(button => {
            button.onclick = () => {
                const channel = button.innerHTML;
                sessionStorage.setItem('channel', channel);
            };
        });

    });

    socket.on('announce_message', data => {
        var current_channel = sessionStorage.getItem('channel')
        // if current channel recieves a message
        if (current_channel === data.channel) {
            var ul = document.getElementById("messages-list");
            // if message was previously dequeued, remove it on the page
            if (data.delete_message == true) {
                document.getElementById("messages-list").removeChild(document.getElementById("messages-list").children[0])
            }
            // Add new li of new message
            const li = document.createElement('li');
            li.innerHTML = `${data.user}: ${data.message}
            
            Time: ${data.timestamp}`
            // Add new item to task list
            ul.appendChild(li)
            // Clear input field
            document.querySelector('#new_message').value = '';
        }
    });
});
