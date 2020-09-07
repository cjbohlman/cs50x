


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
            var from_user = sessionStorage.getItem('username')
            var to_user = sessionStorage.getItem('to_user')
            var message = document.querySelector('#new_message').value
            const timestamp = new Date().toUTCString();
            if (!from_user || from_user === "") {
                from_user = "blank"
            }
            if (message === "") {
                return false;
            }

            socket.emit('new user message', {'from_user': from_user, 'to_user': to_user,'message': message, 'timestamp': timestamp});
            return false;
        };

        document.querySelectorAll('#view_user').forEach(button => {
            button.onclick = () => {
                const to_user = button.innerHTML;
                sessionStorage.setItem('to_user', to_user);
                document.getElementById("add_message").style.visibility = "visible"; 
                document.getElementById("messages").style.visibility = "visible"; 
            };
        });

    });

    socket.on('announce_user_message', data => {
        var current_user_pm = sessionStorage.getItem('to_user')
        // if current channel recieves a message
        if (current_user_pm === data.to_user) {
            var ul = document.getElementById("messages-list");
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
