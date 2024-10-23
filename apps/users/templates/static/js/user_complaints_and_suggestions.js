$(document).ready(function() {
    $('body').fadeIn(1000);
});

$('#sent-complaint-suggestion').on('click', async function(event){
    event.preventDefault();

    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    //const url = 'http://127.0.0.1:8000/';
    const url = 'https://django-chatbot-quejas-y-sugerencias.onrender.com/';

    const response = await fetch(url+'complaint_suggestion/', {
        method: 'POST',
        mode: 'same-origin',
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            name: $('#name').val(),
            email: $('#email').val(),
            complaint_suggestion: $('#complaint-suggestion').val()
        })
    }).then(async (response) => {

        if (response.status === 201) {
            return response.json();
        }else{
            $('#message').show().delay(3000).fadeOut();
            throw new Error('Request failed with status');
        }
    
    }).catch(error => {
        console.error('Error:', error);
    });

})
