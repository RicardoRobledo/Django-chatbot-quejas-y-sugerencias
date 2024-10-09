//const url = 'http://127.0.0.1:8000';
const url = 'https://django-chatbot-quejas-y-sugerencias.onrender.com';

const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

let image_id = 0;


$(document).ready(async function () {

    const loaderText = document.querySelector('.loader-text');
    const texts = ['Procesando la información', 'Por favor espere un poco...', '...'];
    let currentIndex = 0;

    intializeComponents();

    function changeText() {
        loaderText.style.opacity = '0';

        setTimeout(() => {
            currentIndex = (currentIndex + 1) % texts.length;
            loaderText.textContent = texts[currentIndex];
            loaderText.style.opacity = '1';
        }, 500);
    }

    setInterval(changeText, 4000);

    const initialYear = 2015;
    const actualYear = new Date().getFullYear();
    const yearSpinner = $('#select-year');

    for (let year = actualYear; year >= initialYear; year--) {
        yearSpinner.append(`<option value="${year}">${year}</option>`)
    }

    $('#select-year').val(actualYear);
    
    const response = await getYearStatistics(actualYear);

    response['data']['number_complaints_suggestions_by_month'].forEach((element, index) => {

        index++;

        $('#table-body').append(`
            <tr>
                <td id="month">${element['month']}</td>
                <td class="center-text number-complaints-suggestions">${element['number_complaints_suggestions']}</td>
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

function intializeComponents(){
    $('#btn-consult').prop( "disabled", true);
}

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

async function getYearStatistics(year){

    const response = await fetch(`${url}/custom_admin/admin/statistics/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({ 'year': parseInt(year) })
    }).then(response => response.json());

    return response;

}

function changeRadioButtonSelected(id) {
    $('#btn-consult').prop("disabled", false);
};

$('#select-year').change(function() {
    // Obtener el valor seleccionado
    let selectedYear = $(this).val();
    
    // Verificar si se seleccionó un año
    if (selectedYear) {
        $('#btn-consult-year').prop("disabled", false);
        $('#table-body td[class="number-complaints-suggestions"]').text(0);
        $('#table-body .number-complaints-suggestions').each(function() {$(this).text(0);});
    } else {
        $('#btn-consult-year').prop("disabled", true);
        $('#btn-consult').prop("disabled", true);
    }

    $('#table-body input[type="radio"]').prop('disabled', true);

});

$('#btn-consult-year').click(async function(event) {

    event.preventDefault();

    $('.loader-container').show();
    $('.content-container').hide();

    $('#table-body').html('');

    const year = $('#select-year').val();
    const response = await getYearStatistics(year);

    response['data']['number_complaints_suggestions_by_month'].forEach((element, index) => {

        index++;

        $('#table-body').append(`
            <tr>
                <td id="month">${element['month']}</td>
                <td class="center-text number-complaints-suggestions">${element['number_complaints_suggestions']}</td>
                <td class="radio-cell"><input id="${index}" onclick="changeRadioButtonSelected('${index}')" type="radio" name="month" class="radio-column" disabled></td>
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

    $('#table-body input[type="radio"]').prop('disabled', false);

});

$('#btn-consult').click(async function(event) {

    event.preventDefault();

    $('.loader-container').show();
    $('.content-container').hide();

    let month = $('input[name="month"]:checked').attr('id');
    let selectedYear = $('#select-year').val();
    
    const response = await fetch(`${url}/custom_admin/admin/statistics/month-year/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({ 'month': parseInt(month), 'year': parseInt(selectedYear) })
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
