function load_graph(hr){
    var now = Math.floor(Date.now() / 1000);
    var start_time = now - (hr*3600);

    var image_holder = document.getElementById("graph");
    image_holder.src = 'http://127.0.0.1:2020/climate/graph?start_time=' + start_time;
    alert('Image source set try 8')
}