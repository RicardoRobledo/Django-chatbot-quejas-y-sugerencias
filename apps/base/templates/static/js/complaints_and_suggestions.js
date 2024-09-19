const url = 'http://127.0.0.1:8000';
//const url = 'https://django-chatbot-quejas-y-sugerencias.onrender.com';

const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

let image_id = 0;


$(document).ready(async function () {
    $('#btn-consult').prop( "disabled", true);

    const loaderText = document.querySelector('.loader-text');
    const texts = ['Procesando la información', 'Por favor espere un poco...', '...'];
    let currentIndex = 0;

    function changeText() {
        loaderText.style.opacity = '0';

        setTimeout(() => {
            currentIndex = (currentIndex + 1) % texts.length;
            loaderText.textContent = texts[currentIndex];
            loaderText.style.opacity = '1';
        }, 500);
    }

    setInterval(changeText, 4000);

    const response = await fetch(`${url}/custom_admin/admin/statistics/`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        }
    }).then(response => response.json());

    response['data']['number_complaints_suggestions_by_month'].forEach((element, index) => {

        index++;

        $('#table-body').append(`
            <tr>
                <td id="month">${element['month']}</td>
                <td id="number-complaints-suggestions" class="center-text">${element['number_complaints_suggestions']}</td>
                <td class="radio-cell"><input id="${index}" onclick="changeRadioButtonSelected('${index}')" type="radio" name="month" class="radio-column"></td>
            </tr>
        `);
    });

    const complaints_graph = response['data']['complaints_response']['graph']
    const suggestions_graph = response['data']['suggestions_response']['graph']

    $('.right-section').html(`
        <img class="responsive-image" src="data:image/png;base64,${complaints_graph}" class="img-fluid" id="chart-image-${image_id}">
        <button id="download-image" class="default" onclick="downloadImage(${image_id++})">Descargar imagen</button>
        <img class="responsive-image" src="data:image/png;base64,${suggestions_graph}" class="img-fluid" id="chart-image-${image_id}">
        <button id="download-image" class="default" onclick="downloadImage(${image_id++})">Descargar imagen</button>`);

    $('.loader-container').fadeOut(1000);
    $('.content-container').fadeIn(3000);

});

function downloadImage(id) {

    // Obtener la URL de la imagen en base64
    var imgSrc = $(`#chart-image-${id}`).attr('src');
  
    // Crear un enlace de descarga
    var link = $('<a></a>')
      .attr('href', imgSrc)
      .attr('download', `imagen-gráfico-${id}.png`)
      .appendTo('body');
  
    // Simular el clic en el enlace
    link[0].click();

    // Eliminar el enlace después de la descarga
    link.remove();
  
};

function changeRadioButtonSelected(id) {
    $('#btn-consult').prop("disabled", false);
};


$('#btn-consult').click(async function(event) {

    event.preventDefault();

    $('.loader-container').show();
    $('.content-container').hide();

    var month = $('input[name="month"]:checked').attr('id');
    
    const response = await fetch(`${url}/custom_admin/admin/statistics/${month}/`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        }
    }).then(response => response.json());

    const complaints_graph = response['data']['complaints_response']['graph']
    const suggestions_graph = response['data']['suggestions_response']['graph']

    $('.right-section').html(`
        <img class="responsive-image" src="data:image/png;base64,${complaints_graph}" class="img-fluid" id="chart-image-${image_id}">
        <button id="download-image" class="default" onclick="downloadImage(${image_id++})">Descargar imagen</button>
        <img class="responsive-image" src="data:image/png;base64,${suggestions_graph}" class="img-fluid" id="chart-image-${image_id}">
        <button id="download-image" class="default" onclick="downloadImage(${image_id++})">Descargar imagen</button>`);

    $('.loader-container').fadeOut(1000);
    $('.content-container').fadeIn(3000);

});
