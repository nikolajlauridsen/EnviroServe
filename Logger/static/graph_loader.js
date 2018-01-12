function load_graph(hr){
    var now = Math.floor(Date.now() / 1000);
    var start_time = now - (hr*3600);

    var XHR = new XMLHttpRequest();
    var FD = new FormData();

    FD.append('start_time', start_time.toString());

    // Define what happens on successful load
    XHR.addEventListener('load', function(event){
        var img = document.getElementById("graph");
        var image = new Image();
        image.src = XHR.src;
        img.load(image);
        alert('Image should be loaded now pliz');
    });

    // Handle error
    XHR.addEventListener('error', function(event){
        alert('Something went wrong...');
    });

    // Set up request
    XHR.open('GET', 'http://127.0.0.1:2020/climate/graph');
    // Send it
    XHR.send(FD);
}