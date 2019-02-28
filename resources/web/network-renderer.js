let networkDiv = document.getElementById("network-div");

let app = new PIXI.Application({
    width: networkDiv.offsetWidth,
    height: networkDiv.offsetHeight,
    antialias: true,
    transparent: true
});

let stage = app.stage;
networkDiv.appendChild(app.view);

function init(scene) {
    $.ajaxSetup({async: false});

    $.when(
        initData(),
    ).then(
        initScene(scene)
    );

    $.ajaxSetup({async: true});
}

function initScene(scene) {
    loops.forEach(function (aLoop) {
        aLoop.object.drawInto(scene);
    });

    stations.forEach(function (aStation) {
        aStation.object.drawInto(scene);
    });

    switches.forEach(function (aSwitch) {
        aSwitch.object.drawInto(scene);
    });
}

function update(scene) {
    console.log('update');
    $.ajaxSetup({async: false});

    $.when(
        updateData()
    ).then(
        updateScene(scene)
    );

    $.ajaxSetup({async: true});
}

function updateScene(scene) {
    /*stations.forEach(function (aStation) {
    });

    switches.forEach(function (aSwitch) {
    });*/

    capsules.forEach(function (aCapsule) {
        aCapsule.object.drawInto(scene);
    });
}

init(stage);

setInterval(() => {
    updateData();
}, 50);
/*
for (let i = 0; i < 2; i++) {
    if (scene !== undefined)
        app.stage.removeChild(scene);

    scene = new PIXI.Container();

    app.stage.addChild(scene);
    console.log(scene.children.length)
}*/




