document.addEventListener('DOMContentLoaded', () => {
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);
    // When connected, configure buttons
    socket.on('connect', () => {
        // // Add message event
        // document.querySelector('#add_message').onsubmit = () => {
        //     const user = localStorage.getItem('username')
        //     const message = document.querySelector('#new_message')
        //     const timestamp = Date.now
        //     socket.emit('new message', {'user': user, 'message': message, 'timestamp': timestamp});
        //     return false;
        // };
        // Add channel event
        // document.querySelector('#add_channel').onsubmit = () => {
        //     const channel_name = document.querySelector('#new_channel').value;
        //     socket.emit('new channel', {'name': channel_name});
        //     // Stop form from submitting
        //     return false;
        // };
    });

    // // When a new message is added, add to the list
    // socket.on('announce message', data => {
    //     const li = document.createElement('li');
    //     li.innerHTML = `${data.user}: ${data.message}
    //     Time: ${data.timestamp}`;
    //     document.querySelector('#messages').append(li);
    // });

    // When a new vote is announced, add to the unordered list
    socket.on('announce channel', data => {
        // Create new item for list
        var a = document.createElement("a");
        const li = document.createElement('li');
        a.textContent = document.querySelector('#new_channel').value;
        a.setAttribute('class', "nav-link");
        a.setAttribute('href', '')
        a.setAttribute('data-page',document.querySelector('#new_channel').value);
        li.appendChild(a);
        // Add new item to task list
        document.querySelector('#channel-list').append(li);
        // Clear input field
        document.querySelector('#new_channel').value = '';
        // Link to channel
        document.querySelectorAll('.nav-link').forEach(link => {
            link.onclick = () => {
                localStorage.setItem('channel', link.dataset.page)
                load_page(link.dataset.page);
                return false;
            };
        });
    });

    // Renders contents of new page in main view.
    function load_messages(name) {
        const request = new XMLHttpRequest();
        request.open('GET', `/channel/${name}`);
        request.onload = () => {
            const response = request.responseText;
            document.querySelector('#body').innerHTML = response;
        };
        request.send();
    }
});