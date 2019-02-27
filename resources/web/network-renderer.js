let networkDiv = document.getElementById("network-div");

let app = new PIXI.Application({
    width: networkDiv.offsetWidth,
    height: networkDiv.offsetHeight,
    antialias: true,
    transparent: true
});

let stage = app.stage;
networkDiv.appendChild(app.view);

function init() {
    $.when($.ajax(initData())).then(initScene);
}

function initScene() {
    loops.forEach(function(loop) {
        loop.object.drawInto(stage);
    });

    stations.forEach(function(station) {
        station.object.drawInto(stage);
    });

    switches.forEach(function(switches) {
        switches.object.drawInto(stage);
    });
}


function update() {

}

init();




