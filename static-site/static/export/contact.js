document.getElementById('contact_form').addEventListener('submit', function(event) {
    event.preventDefault();
    if (!this.reportValidity()) return;
    const values = new FormData(this);
    const name = [values.get('first_name'), values.get('last_name')].filter(Boolean).join(' ');
    const message = 'Hello, I am ' + name + '.\n\nEmail: ' + values.get('email') + '\n\nMessage: ' + values.get('description');
    window.location.assign('https://wa.me/918750971212?text=' + encodeURIComponent(message));
});