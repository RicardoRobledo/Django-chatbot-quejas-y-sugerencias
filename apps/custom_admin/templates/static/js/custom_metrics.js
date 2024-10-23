const url = 'http://127.0.0.1:8000';
//const url = 'https://django-chatbot-quejas-y-sugerencias.onrender.com';

const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;


$(document).ready(function() {
    $('#content-container').show();
    $('#home-loader').remove();
});

$('input[type="checkbox"]').on('change', function() {
    var relatedInput = $(this).closest('.mb-3').find('input[type="text"]');
    if ($(this).is(':checked')) {
        relatedInput.prop('disabled', false);
        relatedInput.css('background-color', '#8a56ac');
    } else {
        relatedInput.prop('disabled', true);
        relatedInput.css('background-color', '#E9ECEF');
    }
});


$('#add-complaint-button').on('click', async function() {

    var checkedFields = [];

    $('#form-complaints input[type="checkbox"]').each(function() {
        var relatedInput = $(this).closest('.mb-3').find('input[type="text"]');
        checkedFields.push(relatedInput.val());
    });

    const response = await fetch(`${url}/custom-admin/admin/update_complaint_types_view/`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({
            complaints: checkedFields
        })
    }).then(
        response => response.json()
    ).then(data => data);

});

$('#add-suggestion-button').on('click', async function() {

    var checkedFields = [];

    $('#form-suggestions input[type="checkbox"]').each(function() {
        var relatedInput = $(this).closest('.mb-3').find('input[type="text"]');
        checkedFields.push(relatedInput.val());
    });

    const response = await fetch(`${url}/custom-admin/admin/update_suggestion_types_view/`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({
            suggestions: checkedFields
        })
    }).then(
        response => response.json()
    ).then(data => data);

});
