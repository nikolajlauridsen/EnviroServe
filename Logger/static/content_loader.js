function load_graph(days, hours){
    var duration = days * 24 * 3600 + hours * 3600;
    // Gets unix time string.
    var now = Math.floor(Date.now() / 1000);
    var start_time = now - duration;

    var image_holder = document.getElementById("graph");
    var graph_title_holder = document.getElementById("graph title");

    graph_title_holder.innerText = "Graph from: " + format_unix(start_time) + " to: " + format_unix(now);
    image_holder.src = 'http://192.168.1.250:2020/climate/graph?start_time=' + start_time;
}

function load_custom_graph(){
    // Simple "wrapper" function which fetches the values.
    // from the modal, for load_graph, it also closes the modal.
    var hours = document.getElementById("hours").value;
    var days = document.getElementById("days").value;

    load_graph(days, hours);
    $('.modal').modal('close');
}

function format_unix(timestamp){
    var date = new Date(timestamp * 1000);

    // Format time string cause it's weird
    var timestring = date.toLocaleTimeString();
    timestring = timestring.slice(0, timestring.length-3);  // Slice seconds.
    timestring = timestring.replace(".", ":");              // Replace . with :

    return timestring + " " + date.toLocaleDateString();
}

function graph_data() {
    // Get data from API
    var url = "http://127.0.0.1:2020/climate/data";
    // Get data from last week
    var start_time = Math.floor(Date.now()/1000) - 3600*24*7;
    url += "?start_time=" + start_time;
    $.getJSON(url, '', function (json) {
        // Retrieve the data from the json
        var data_result = json.results;
        // Lists for holding values, makes them easier to graph
        var temps = [];
        // Iterate over the results list sorting the values into their list
        for(var i =0; i < data_result.length; i++){
            temps.push([new Date(data_result[i].time*1000), parseFloat(data_result[i].temp),
                        parseFloat(data_result[i].humid), parseFloat(data_result[i].pressure)]);
        }
        //It's finally time to graph the data
        // Load the Visualization API and the corechart package.
        google.charts.load('current', {'packages':['line']});

        // Set a callback to run when the Google Visualization API is loaded.
        google.charts.setOnLoadCallback(drawChart);
        function drawChart() {
            var data = new google.visualization.DataTable();
            data.addColumn('date', 'Time');
            data.addColumn('number', 'Temperature');
            data.addColumn('number', 'Humidity');
            data.addColumn('number', 'Pressure');
            data.addRows(temps);
            // Set options
            var options = {chart: {'title': 'Climate graph'},
                           'width': 900,
                           'height': 600,
                           'series': {
                                0: {axis: 'Temps'},
                                1: {axis: 'Temps'},
                                2: {axis: 'Pressure'}
                            },
                            axes: {
                                y: {Temps: {label: 'Temp/Humidity'},
                                    Pressure: {label: 'Pressure'}}
                            }};
            // Instansiate and draw chart
            var chart = new google.charts.Line(document.getElementById('climateChart'));
            chart.draw(data, google.charts.Line.convertOptions(options));
        }
    });
}

$(document).ready(function () {
    // Activates modal and loads extra page elements.
    $('.modal').modal();
    graph_data()
});
