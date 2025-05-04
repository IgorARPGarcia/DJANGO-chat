document.getElementById('room-form').onsubmit = function(e) {
    e.preventDefault();
    const roomName = document.getElementById('room-name').value;
    window.location.href = `/chat/${roomName}/`;
};