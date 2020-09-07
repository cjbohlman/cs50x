document.addEventListener('DOMContentLoaded', () => {
    if(sessionStorage.getItem('username')) {
        if (localStorage.getItem('lastchannel')) {
            load_page('channel/'+localStorage.getItem('lastchannel'))
        }
        else {
            load_page('home')
        }
        
    } else {
        document.getElementById('login').onsubmit = () => {
            const user = document.querySelector('#username').value
            sessionStorage.setItem('username', user);
            const request = new XMLHttpRequest();
            request.open('POST', `/user/${user}`);
            request.send()
        };
    }

    function load_page(name) {
        const request = new XMLHttpRequest();
        request.open('GET', `/${name}`);
        request.onload = () => {
            const response = request.responseText;
            document.querySelector('body').innerHTML = response;
            if (!sessionStorage.getItem("channel")) {
                document.getElementById("add_message").style.visibility = "hidden"; 
                document.getElementById("messages").style.visibility = "hidden"; 
            }
        };
        request.send();
    }
});