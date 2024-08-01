//const url = 'http://127.0.0.1:8000/';
const url = 'https://django-chatbot-quejas-y-sugerencias.onrender.com/';
const assistant_name = 'Asistente de quejas';
const welcome_message = '👋 ¡Hola!, ¿Que necesitas saber el día de hoy?';
let message_id = 0;
let image_id = 0;
let word_id = 0;
const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
const md = window.markdownit();


// --------------------------------------------------
//                    functions
// --------------------------------------------------

function format_chatbot_message(id) {

  const chatbotMessage = `
  <div class='chatbot-message col-12 py-4 d-flex justify-content-center' id='${id}' style='display:none;'>
      <div class='d-flex col-8' id='chatbot-message-content'>
          <img src='/static/imgs/chatbot.jpeg' width='60' height='60'>
          <div class='m-2'>
              <h6>${assistant_name}</h6>
              <p></p>
              <div class='container-animacion'>
                <div class='cargando'>
                  <div class='pelotas'></div>
                  <div class='pelotas'></div>
                  <div class='pelotas'></div>
                </div>
              </div>
          </div>
      </div>
  </div>`;

  return chatbotMessage;

}


function format_user_message(message) {

  const userMessage = `
  <div class='user-message col-12 py-4 d-flex justify-content-center'>
      <div class='d-flex col-8' id='user-message-content'>
          <img src='/static/imgs/admin.png' width='60' height='60'>
          <div class='m-2'>
              <h6>Tú</h6>
              <p>${message}</p>
          </div>
      </div>
  </div>`;

  return userMessage;

}


function hide_message_container() {
  $('#btn-enviar').hide();
  $('#input-message').hide();
}


function disable_form_message() {
  $('#btn-detener').show();
  $('#btn-enviar').hide();
  $('#input-message').prop('disabled', true);
}


function enable_form_message() {
  let send_button = $('#btn-enviar');
  send_button.css('color', '#000000');
  send_button.css('background-color', '#c5c5c5');
  send_button.prop('disabled', true);
  send_button.show();
  $('#btn-detener').hide();
  $('#input-message').prop('disabled', false);
}


async function initialize() {

  let send_button = $('#btn-enviar');
  send_button.css('background-color', '#c5c5c5');
  send_button.css('color', '#000000');
  send_button.prop('disabled', true);
  $('#btn-detener').hide();
  hide_message_container();
  $('#initial-cards-container').hide();

}


async function downloadImage(id) {

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


async function downloadWord(id) {

  const { Document, Packer, Table, TableRow, TableCell, WidthType, Paragraph } = docx;

  const table = $(`#word-table-${id} table`)[0];

  function createWordTable(htmlTable) {
    const rows = $(htmlTable).find('tr').get();
    const docxRows = rows.map(row => {
      const cells = $(row).find('th, td').get();
      const docxCells = cells.map(cell => new TableCell({
        children: [new Paragraph($(cell).text())],
      }));
      return new TableRow({
        children: docxCells,
      });
    });

    return new Table({
      rows: docxRows,
      width: {
        size: 100,
        type: WidthType.PERCENTAGE,
      },
    });
  }

  const docTable = createWordTable(table);

  const doc = new Document({
    sections: [{
      children: [docTable],
    }],
  });

  // Empaquetar el documento para ser descargado
  Packer.toBlob(doc).then(blob => {
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `documento-word-${id}.docx`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  });

};

function get_message() {
  const message = $('#input-message').val();
  $('#input-message').val('');
  return message;
}


async function send_message(id, user_message, signal) {

  const message_url = url + 'chatbot/message/';
  const thread_id = localStorage.getItem('thread_id');

  const response = await fetch(message_url, {
    signal: signal,
    method: 'POST',
    mode: 'same-origin',
    headers: {
      'X-CSRFToken': csrftoken,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ thread_id, user_message })
  }).then(async (response) => {

    if (response.status === 402) {
      throw new PaymentRequiredError('Error, se ha alcanzado alcanzado el límite de saldo');
    } else {
      return response.json();
    }

  }).then(
    async (data) => {

      const msg = data['msg'];
      let resultHtml = '';

      const parser = new DOMParser();
      const doc = parser.parseFromString(msg, 'text/html');

      if ('img' in data) {

        resultHtml = md.render(msg);
        $(`#${id} .m-2`).append(resultHtml);
        $(`#${id} .m-2`).append(`
          <div class="text-center">
            <img src="data:image/png;base64,${data['img']}" class="img-fluid" id="chart-image-${image_id}">
            <button id="download-image" class="btn btn-info text-white mt-5" onclick="downloadImage(${image_id++})">Descargar imagen</button>
          </div>`);

      } else if (Array.from(doc.body.childNodes).some(node => node.nodeType === 1)) {

        const table = `
        <div class="card">
    <div class="card-header d-flex justify-content-between">
      <p class="fw-semibold">Tabla generada</p>
      <button id="downloadPdf" class="btn btn-info text-white mt-3" onclick="downloadWord(${image_id})">Descargar Word</button>
    </div>
    <div class="card-body">
      <div class="container">
        <div class="table-responsive" id="word-table-${word_id++}">
          ${doc.body.innerHTML}
        </div>
      </div>
    </div>
  </div>`;

        $(`#${id} .m-2 p`).html(table);
        $('table').addClass('table table-warning table-bordered table-hover');
        $(`#${id} #chatbot-message-content`).addClass('flex-column');

      } else {

        resultHtml = md.render(msg);
        $(`#${id} .m-2 p`).append(resultHtml);

      }

    }
  ).catch(error => {

    if (error.name === 'AbortError') {
      $(`#${id} .m-2 p`).append('<h7 class="text-secondary">Mensaje detenido<h7>');
    } else if (error.name === 'PaymentRequiredError') {
      $(`#${id} .m-2 p`).append('<h7 class="text-danger">Error, el límite de cuota ha sido alcanzado, por favor verifique su crédito<h7>');
    } else {
      $(`#${id} .m-2 p`).append('<h7 class="text-danger">Hubo un error en el mensaje<h7>');
    }

  });

  return response;
}


async function create_conversation_thread(fromDate, toDate) {

  const response = await fetch(url + 'chatbot/thread_id/', {

    method: 'POST',
    mode: 'same-origin',
    headers: {
      'X-CSRFToken': csrftoken,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ 'dates': { 'from_date': fromDate, 'to_date': toDate } })

  }).then(async (response) => {

    if (response.status === 200) {
      return response.json();
    }else if (response.status === 500) {
      throw new CustomError('ThreadError', 'Error al crear el hilo de conversación');
    }

  }).then(async (data) => {

    $('#btn-enviar').fadeIn(900)
    $('#input-message').show(900);
    $('#form-calendar').hide();
    $('#message-container p').remove();
    $('#message-container form').remove();
    $('#success-tokens-badge').fadeIn(900);
    $('#success-date-badge').fadeIn(900);
    $('#initial-cards-container').fadeIn(900);

    const num_tokens = data['num_tokens'];

    if(num_tokens<=2906){
      $('#success-tokens-badge').text(`Tokens: ${num_tokens}`);
      $('#success-tokens-badge').addClass('text-bg-primary');
    }else{
      $('#success-tokens-badge').text(`Tokens: ${num_tokens}`);
      $('#success-tokens-badge').addClass('text-bg-danger');
    }

    localStorage.setItem('num_token', num_tokens);
    localStorage.setItem('thread_id', data['thread_id']);

    return data;

  }).catch(error => {

    if (error.name === 'ThreadError') {
      $('#ThreadErrorModal').modal('show');
    } 

  });

}


async function delete_conversation_thread() {

  if (localStorage.getItem('thread_id') !== null) {

    var requestOptions = {
      method: 'POST',
      mode: 'same-origin',
      headers: {
        'X-CSRFToken': csrftoken,
        'Content-Type': 'application/json',
      }
    };

    const thread_url = url + 'chatbot/thread_id/' + localStorage.getItem('thread_id') + '/'
    navigator.sendBeacon(thread_url, requestOptions);

    localStorage.removeItem('thread_id');

  }

}


// --------------------------------------------------
//                      events
// --------------------------------------------------


$('.initial-message-container').on('click', function () {
  const text = $(this).find('.card-text').text();
  $('#initial-cards-container').hide();
  enable_form_message();
  $('#input-message').val(text);
  $('#btn-enviar').click();
  disable_form_message();
});


$('#input-message').on('keyup', function (event) {

  let text = $(this).val();
  let button = $('#btn-enviar');

  if (text.trim() === "") {
    button.css('color', '#000000');
    button.css('background-color', '#c5c5c5');
    button.prop('disabled', true);
  } else {
    if (event.keyCode === 13) {
      button.trigger('click');
    }

    button.css('color', '#ffffff');
    button.css('background-color', '#007bff');
    button.prop('disabled', false);
  }

});


$('#confirm-button').click(async function (event) {

  event.preventDefault();

  function isValidDate(date) {
    return date instanceof Date && !isNaN(date);
  }

  const fromDate = new Date($('#datepicker').val());
  const toDate = new Date($('#datepicker2').val());

  if (!isValidDate(fromDate) || !isValidDate(toDate)) {

    $('#warning-badge').text('Una o ambas fechas son inválidas');
    $('#warning-badge').fadeIn(900, function () {
      $(this).delay(2000).fadeOut(900);
    });

  } else if (fromDate > toDate) {

    $('#warning-badge').text('La fecha inicial no puede ser mayor a la fecha final');
    $('#warning-badge').fadeIn(900, function () {
      $(this).delay(2000).fadeOut(900);
    });

  } else {

    await create_conversation_thread(fromDate, toDate);

  }

});


$('#btn-logout').click(async function (event) {

  await delete_conversation_thread();
  window.location.href = '/authentication/login/';

});


$('#btn-enviar').on('click', async function () {

  $('#initial-cards-container').hide();
  disable_form_message();
  const userMessage = get_message();
  // getting identifier to add in chatbot message
  const id = 'container-chatbot-message-' + message_id++;
  const formattedChatbotMessage = format_chatbot_message(id);
  const formattedUserMessage = format_user_message(userMessage);

  // adding messages to conversation
  $('.conversation').append(formattedUserMessage);
  $('.conversation').append(formattedChatbotMessage);

  window.scrollTo(0, document.documentElement.scrollHeight);

  // sending message to chatbot
  controller = new AbortController();
  const signal = controller.signal;
  const response = await send_message(id, userMessage, signal);

  $('.container-animacion').remove();
  $(`#${id}`).fadeIn();

  window.scrollTo(0, document.documentElement.scrollHeight);

  enable_form_message();

});


$('#btn-detener').on('click', function () {
  enable_form_message();
  if (controller) {
    controller.abort(); // Se llama al método abort() del controlador para cancelar la petición
    console.log('Petición cancelada');
  }
});


$(window).on('beforeunload', async function () {

  if (localStorage.getItem('thread_id') !== null) {
    await delete_conversation_thread();
  }

});


// --------------------------------------------------
//                 custom exceptions
// --------------------------------------------------


class CustomError extends Error {
  constructor(name, message) {
    super(message);
    this.name = name;
  }
}

// Otra clase de error personalizada
class PaymentRequiredError extends CustomError {
  constructor(message) {
    super('PaymentRequiredError', message);
  }
}

// --------------------------------------------------
//                 initialization
// --------------------------------------------------


$(document).ready(async function () {

  await initialize();

  $("h6").text(`{{assistant_name}}`.replace("{{assistant_name}}", assistant_name));

  $(".loader-wrapper").fadeOut(1200, function () {
    $("#contenido").fadeIn(1500);
  });

});

//$( document ).ready(function(){});
//$( window ).on( "load", function(){});