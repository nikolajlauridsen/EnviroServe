function load_graph(hr){
    var now = Math.floor(Date.now() / 1000);
    var start_time = now - (hr*3600);

    var image_holder = document.getElementById("graph");
    image_holder.src = 'http://192.168.1.250:2020/climate/graph?start_time=' + start_time;
}