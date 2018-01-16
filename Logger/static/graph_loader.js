function load_graph(hr){
    var now = Math.floor(Date.now() / 1000);
    var start_time = now - (hr*3600);

    var image_holder = document.getElementById("graph");
    var graph_title_holder = document.getElementById("graph title");

    graph_title_holder.innerText = "Graph from: " + format_unix(start_time) + " to: " + format_unix(now);
    image_holder.src = 'http://192.168.1.250:2020/climate/graph?start_time=' + start_time;
}

function format_unix(timestamp){
    var date = new Date(timestamp * 1000);

    // Format time string cause it's weird
    var timestring = date.toLocaleTimeString();
    timestring = timestring.slice(0, timestring.length-3);  // Slice seconds
    timestring = timestring.replace(".", ":");              // Replace . with :

    return timestring + " " + date.toLocaleDateString();
}
document.addEventListener("DOMContentLoaded", function () {
    load_graph(12);
});
