document.addEventListener('DOMContentLoaded', () => {
    if(localStorage.getItem('username')) {
        load_page('home', localStorage.getItem('username'))
    } else {
        load_page('login')
        document.querySelector('#login').onsubmit = () => {
            localStorage.setItem('username', document.querySelector('#username').value);
        };
    }

    function load_page(name) {
        const request = new XMLHttpRequest();
        request.open('GET', `/${name}`);
        request.onload = () => {
            const response = request.responseText;
            document.querySelector('#body').innerHTML = response;
        };
        request.send();
    }
});