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
$(document).ready(function () {
    // Activates modal and loads extra page elements.
    $('.modal').modal();
    load_graph(0, 12);
});
