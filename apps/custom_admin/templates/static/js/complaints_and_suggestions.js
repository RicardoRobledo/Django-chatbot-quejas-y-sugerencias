const url = 'http://127.0.0.1:8000';
//const url = 'https://django-chatbot-quejas-y-sugerencias.onrender.com';

const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

const barColors = ["#8a56ac", "#4a90e2", "#50e3c2", "#9013fe", "#b8e986"];

const statisticsMap = new Array(12).fill(0);


$(document).ready(async function () {

    const year = $('#select-year').val();
    
    const responseYearMonthStatistics = await getYearMonthStatistics(year);
    const responseYearStatistics = await getYearStatistics(year);

    const [complaintBars, suggestionBars] = await getChartTableData(responseYearMonthStatistics, responseYearStatistics);

    const maxValueComplaint = Math.max(...complaintBars.map(item => item.value));
    const maxValueSuggestion = Math.max(...suggestionBars.map(item => item.value));

    createBarChart(complaintBars, maxValueComplaint, "#bar-chart-complaints", "Quejas");
    createBarChart(suggestionBars, maxValueSuggestion, "#bar-chart-suggestions", "Sugerencias");

    $('#home-loader').fadeOut(3000);
    $('#content-container').fadeIn(3000);

});

async function getChartTableData(responseYearMonthStatistics, responseYearStatistics) {

    const statisticsMapCopied = statisticsMap.slice();

    responseYearMonthStatistics['statistics'].forEach((item) => {
        statisticsMapCopied[item.month - 1] = item.count;
    });

    statisticsMapCopied.forEach((count, index) => {
        let thElement = $(`#month-${index + 1}`);
        let radioElement = thElement.closest('tr').find('input[type="radio"]');

        if (thElement.length) {
            // Actualizar el texto del siguiente elemento de la misma fila
            let thElementCount = thElement.next()
            console.log(count);
            thElementCount.text(count);
    
            if (count === 0) {
                // Deshabilitar el radio button si el count es cero
                radioElement.prop('disabled', true);
                thElementCount.css('color', '#b50e3e');
            } else {
                radioElement.prop('disabled', false);
                thElementCount.css('color', '#ffffff');
            }
        }
    });

    $('table input[type="radio"]').prop('checked', false);

    const [complaintBars, suggestionBars] = createBars(responseYearStatistics['complaints_by_type_and_year'], responseYearStatistics['suggestions_by_type_and_year']);

    return [complaintBars, suggestionBars]

}

function createBars(complaintsIterator, suggestionsIterator){

    const complaintBars = complaintsIterator.map((item, index) => {
        return {
            type: item['type'],
            value: item['count'],
            color: barColors[index]
        };
    });

    const suggestionBars = suggestionsIterator.map((item, index) => {
        return {
            type: item['type'],
            value: item['count'],
            color: barColors[index]
        };
    });

    return [complaintBars, suggestionBars]

}

async function createBarChart(data, maxValue, selector, chartTitle) {

    $(selector).empty();

    const width = 300;
    const height = 200;
    const margin = { top: 40, right: 30, bottom: 20, left: 30 };

    // Crear el SVG contenedor
    const svg = d3.select(selector)
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    // Escalas para el gráfico
    const x = d3.scaleBand()
        .domain(data.map((d, i) => i))
        .range([0, width])
        .padding(0.2);

    const y = d3.scaleLinear()
        .domain([0, maxValue])
        .nice()
        .range([height, 0]);
    
    const yAxis = d3.axisLeft(y)
        .tickValues(d3.range(0, maxValue + 1, 1))
        .tickFormat(d3.format('d'));

    // Ejes
    svg.append("g")
        .attr("class", "x-axis")
        .attr("transform", `translate(0,${height})`)
        .call(d3.axisBottom(x).tickFormat((d, i) => data[i].name))
        .selectAll("text")
        .attr("class", "axis-label")
        .style("text-anchor", "middle")
        .style("font-size", "15px")
        .style("fill", "#aaa"); // Cambia el color del texto del eje x

    svg.append("g")
        .call(yAxis)
        .selectAll("text")
        .style("fill", "#aaa");

    // Añadir el título del gráfico
    svg.append("text")
        .attr("x", width/2)
        .attr("y", -20)
        .attr("text-anchor", "middle")
        .attr("class", "chart-title-inner") // Usar una clase específica para el título
        .style("font-size", "15px")
        .style("fill", "#aaa")
        .text(chartTitle);

    // Crear las barras
    svg.selectAll(".bar")
        .data(data)
        .enter()
        .append("rect")
        .attr("class", "bar")
        .attr("x", (d, i) => x(i))
        .attr("y", d => y(d.value))
        .attr("width", x.bandwidth())
        .attr("height", d => height - y(d.value))
        .attr("rx", 5)
        .attr("ry", 5)
        .style("fill", d => d.color)
        .on('click', async function (event, d) {

            const year = $('#select-year').val();
            let month = $('input[name="selectedMonth"]:checked');

            if(month.length>0){
                month = month.val();
            }else{
                month = null;
            }

            $('.bar').attr('fill', function() {
                return $(this).data('color');
            });

            $(this).attr('fill', '#FFF');

            let data = null;

            if(chartTitle === 'Quejas') {
                data = (await getSpecificComplaints(year, month, d.type))['complaints'];
            }else{
                data = (await getSpecificSuggestions(year, month, d.type))['suggestions'];
            }

            const cardsHTML = data.reduce((html, obj) => {
                return html + `
                  <div class="card border-secondary mb-3 rounded" style="background-color: #2c2c3e;">
                    <div class="card-header rounded-0">
                      <p class="mb-0 text-white">Fecha: ${obj.year}</p>
                    </div>
                    <div class="card-body">
                      <p class="text-white">Descripción: <i>${obj.description}</i></p>
                    </div>
                    <div class="card-footer">
                      <p class="text-white">Nombre: ${obj.name || '<label class="text-danger">No proporcionado</label>'}</p>
                      <p class="text-white">Correo: ${obj.email || '<label class="text-danger">No proporcionado</label>'}</p>
                    </div>
                  </div>
                `;
              }, '');

            const offcanvasElement = new bootstrap.Offcanvas($('#bar-details')[0]);
            $('#barDetailsLabel').text(d.type);
            $('#bar-details-content').html(cardsHTML);
            offcanvasElement.show();
        })
        .on('mouseover', function (event, d) {
            d3.select(this).attr('fill', d3.rgb(d.color).brighter(0.7)).style('filter', 'brightness(1.3)'); // Aclara el color y ajusta el brillo al hacer hover
        })
        .on('mouseout', function (event, d) {
            d3.select(this).attr('fill', d.color).style('filter', ''); // Devuelve al color original cuando el ratón se aleja
        });
}

async function getYearStatistics(year){

    const response = await fetch(`${url}/custom-admin/admin/statistics/${year}/`, {
        method: 'GET',
        headers: {
            'X-CSRFToken': csrftoken
        },
    }).then(
        response=>response.json()
    ).then(data=>data);

    return response;

}

async function getYearMonthStatistics(year){

    const response = await fetch(`${url}/custom-admin/admin/statistics/year-month/${year}/`, {
        method: 'GET',
        headers: {
            'X-CSRFToken': csrftoken
        },
    }).then(
        response=>response.json()
    ).then(data=>data);

    return response;

}

async function getSpecificComplaints(year, month, name){

    let fullUrl = `${url}/custom-admin/admin/specific-complaints?name=${name}&year=${year}`;

    if(month!==null){
        fullUrl+=`&month=${month}`;
    }

    const response = await fetch(fullUrl, {
        method: 'GET',
        headers: {
            'X-CSRFToken': csrftoken
        },
    }).then(
        response=>response.json()
    ).then(data=>data);

    return response;

}

async function getSpecificSuggestions(year, month, name){

    let fullUrl = `${url}/custom-admin/admin/specific-suggestions?name=${name}&year=${year}`;

    if(month!==null){
        fullUrl+=`&month=${month}`;
    }

    const response = await fetch(fullUrl, {
        method: 'GET',
        headers: {
            'X-CSRFToken': csrftoken
        },
    }).then(
        response=>response.json()
    ).then(data=>data);

    return response;

}

$('#select-year').change(async function() {
    // Obtener el valor seleccionado
    let selectedYear = $(this).val();
    $('table tbody tr').find('input[type="radio"]').prop('disabled', true);

    $('#bar-chart-complaints').empty();
    $('#bar-chart-suggestions').empty();
    $('table').hide();
    $('.table-loader-container').css('display', 'flex');
    $('#bar-chart-complaints-loader').css('display', 'flex');
    $('#bar-chart-suggestions-loader').css('display', 'flex');

    // Verificar si se seleccionó un año
    if (selectedYear) {
        $('#table-body td[class="number-complaints-suggestions"]').text(0);
        $('#table-body .number-complaints-suggestions').each(function() {$(this).text(0);});

        const responseYearMonthStatistics = await getYearMonthStatistics(selectedYear);
        const responseYearStatistics = await getYearStatistics(selectedYear);

        const [complaintBars, suggestionBars] = await getChartTableData(responseYearMonthStatistics, responseYearStatistics);

        const maxValueComplaint = Math.max(...complaintBars.map(item => item.value));
        const maxValueSuggestion = Math.max(...suggestionBars.map(item => item.value));

        createBarChart(complaintBars, maxValueComplaint, "#bar-chart-complaints", "Quejas");
        createBarChart(suggestionBars, maxValueSuggestion, "#bar-chart-suggestions", "Sugerencias");

        $('#bar-chart-complaints-loader').hide();
        $('#bar-chart-suggestions-loader').hide();
        $('.table-loader-container').hide();
        $('table').show();
    }

    $('#table-body input[type="radio"]').prop('disabled', true);

});


$('table input[type="radio"]').on('change', async function(event) {

    event.preventDefault();

    $('#bar-chart-complaints').empty();
    $('#bar-chart-suggestions').empty();
    $('#bar-chart-complaints-loader').css('display', 'flex');
    $('#bar-chart-suggestions-loader').css('display', 'flex');

    let month = $('table input[type="radio"]:checked').val();
    let selectedYear = $('#select-year').val();

    const response = await fetch(`${url}/custom-admin/admin/statistics/year-month/${selectedYear}/${month}/`, {
        method: 'GET',
        headers: {
            'X-CSRFToken': csrftoken
        },
    }).then(response => response.json()
    ).then(data => data);

    const [complaintBars, suggestionBars] = createBars(response['statistics']['complaint_statistics'], response['statistics']['suggestion_statistics']);

    const maxValueComplaint = Math.max(...complaintBars.map(item => item.value));
    const maxValueSuggestion = Math.max(...suggestionBars.map(item => item.value));

    createBarChart(complaintBars, maxValueComplaint, "#bar-chart-complaints", "Quejas");
    createBarChart(suggestionBars, maxValueSuggestion, "#bar-chart-suggestions", "Sugerencias");

    $('#bar-chart-complaints-loader').css('display', 'none');
    $('#bar-chart-suggestions-loader').css('display', 'none');

});

$('#btn-download-excel').on('click', async function() {

    await fetch(`${url}/custom-admin/admin/download-excel-file/`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        }
    }).then(
        response => response.blob()
    ).then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'quejas_y_sugerencias.xlsx';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
    });

});
