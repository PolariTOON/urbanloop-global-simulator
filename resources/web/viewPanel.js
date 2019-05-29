import {Capsule, Loop, Station, Switch, Warehouse, appState, getNetworkDivSize} from "./objects.js";

let viewTab = document.getElementById("view-tab");


function updateViewLoop() {
    let actualLoop = appState.selectedObject;
    let data = "<strong>Vue de la boucle : " + actualLoop.json["name"] + "</strong>" +
    "<div id='view-object' class='container'></div>";
    viewTab.innerHTML = data;

    let stageView = new Konva.Stage({
      container: 'view-object',   // id of container <div>
      width: 200,
      height: 200
    });

    let layer = new Konva.Layer();

    let circle = new Konva.Circle({
      x: stageView.width() / 2,
      y: stageView.height() / 2,
      radius: 70,
      fill: '#ff1eef',
      stroke: 'black',
      strokeWidth: 4
    });

    layer.add(circle);
    stageView.add(layer);
    layer.batchDraw();
    stageView.batchDraw();

}

function updateViewSwitch() {
    let actualSwitch = appState.selectedObject;
    viewTab.innerHTML = "<strong>Vue de l'aiguillage : " + actualSwitch.json["my_loop_name"] + " -> " + actualSwitch.json["other_loop_name"] + "</strong>"
    + "<div id='view-object' class='container'></div>";

    let stageView = new Konva.Stage({
      container: 'view-object',   // id of container <div>
      width: 300,
      height: 300
    });

    let layer = new Konva.Layer();

    let insert = new Konva.Line({
      x: 10,
      y: 10,
      points: [10, 10, 145, 60, 290, 10],
      stroke: 'red',
      strokeWidth: 6,
      tension: 1
    });

    let goal = new Konva.Line({
      x: 10,
      y: 290,
      points: [10, 290, 145, 230, 290, 290],
      stroke: 'blue',
      strokeWidth: 6,
      tension: 1
    });

    layer.add(insert);
    layer.add(goal);
    stageView.add(layer);
    //layer.batchDraw();
    stageView.batchDraw();
}

function updateViewStation() {
    let actualStation = appState.selectedObject;
    viewTab.innerHTML = "<strong>Vue de la station : " + actualStation.json["name"] + "</strong>" +
        "<div id='view-object' class='container'></div>";
}

function updateViewWarehouse() {
    let actualWarehouse = appState.selectedObject;
    viewTab.innerHTML = "<strong>Vue de l'entrepôt n°" + actualWarehouse.json["id"] + "</strong>" +
        "<div id='view-object' class='container'></div>";
}

function updateViewCapsule() {
    let actualCapsule = appState.selectedObject;
    viewTab.innerHTML = "<strong>Vue de la capsule n°" + actualCapsule.json["id"] + "</strong>" +
        "<div id='view-object' class='container'></div>";
}

export async function updateViewPanel() {
    if (appState.selectedObject instanceof Loop)
        updateViewLoop();
    else if (appState.selectedObject instanceof Switch)
        updateViewSwitch();
    else if (appState.selectedObject instanceof Station)
        updateViewStation();
    else if (appState.selectedObject instanceof Warehouse)
        updateViewWarehouse();
    else if (appState.selectedObject instanceof Capsule)
        updateViewCapsule();
}
