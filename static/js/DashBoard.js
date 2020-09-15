var label
var data
var dates
var chartid
var ctx = document.getElementById(chartid).getContext('2d');
var myChart = new Chart(ctx, {
type: 'line',
data: [{
    labels: dates, // вот так выглядит предача данных с бека во фронт(jinja2 фреймворк) Это массив дат по которым показываються данные. 
    datasets: {
        label: label, //Это название самого графика.
        data: data, // это самое главное тут массив данных. 
        backgroundColor: ['rgb(255, 99, 132)'],
        borderColor: ['rgb(255, 99, 132)']
    }]
},

// Configuration options go here
options: {}
});