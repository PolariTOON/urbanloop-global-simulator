import {state} from "./state.js";
import {Loop} from "./loop.js";
import {Switch} from "./switch.js";
import {Station} from "./station.js";
import {Shed} from "./shed.js";
import {Pod} from "./pod.js";
import {Sensor} from "./sensor.js";
const {Circle, Layer, Line, Stage} = Konva;


let viewTab = document.getElementById("view-tab");


function updateViewLoop() {
    let actualLoop = state.selectedObject;
    viewTab.innerHTML = `<strong>Vue de la boucle : ${actualLoop.json["name"]}</strong><div id='view-object' class='container'></div>`;

    let stageView = new Stage({
      container: 'view-object',   // id of container <div>
      width: 200,
      height: 200
    });

    let layer = new Layer();

    let circle = new Circle({
      x: stageView.width() / 2,
      y: stageView.height() / 2,
      radius: 70,
      fill: '#ff1eef',
      stroke: 'black',
      strokeWidth: 4
    });

    layer.add(circle);
    stageView.add(layer);
    stageView.batchDraw();

}

function updateViewSwitch() {
    let actualSwitch = state.selectedObject;
    viewTab.innerHTML = `<strong>Vue de l'aiguillage : ${actualSwitch.json["my_loop_name"]} -> ${actualSwitch.json["other_loop_name"]}</strong><div id='view-object' class='container'></div>`;

    let stageView = new Stage({
      container: 'view-object',   // id of container <div>
      width: 300,
      height: 300
    });

    let layer = new Layer();

    let insert = new Line({
      x: 5,
      y: 10,
      points: [10, 10, 290, 10],
      stroke: '#000000',
      strokeWidth: 6,
      tension: 1
    });

    let goal = new Line({
      x: 5,
      y: 130,
      points: [10, 10, 290, 10],
      stroke: '#000000',
      strokeWidth: 6,
      tension: 1
    });

    let link = new Line({
      x: 5,
      y: 10,
      points: [50, 10, 260, 130],
      stroke: '#000000',
      strokeWidth: 6,
      tension: 1
    });

    layer.add(insert);
    layer.add(goal);
    layer.add(link);
    stageView.add(layer);
}

function updateViewStation() {
    let actualStation = state.selectedObject;
    viewTab.innerHTML = `<strong>Vue de la station : ${actualStation.json["name"]}</strong><div id='view-object' class='container'></div>`;
}

function updateViewShed() {
    let actualShed = state.selectedObject;
    viewTab.innerHTML = `<strong>Vue du dépôt n°${actualShed.json["id"]}</strong><div id='view-object' class='container'></div>`;
}

function updateViewPod() {
    let actualPod = state.selectedObject;
    viewTab.innerHTML = `<strong>Vue de la capsule n°${actualPod.json["id"]}</strong><div id='view-object' class='container'></div>`;
}

function updateViewSensor() {
    let actualSensor = state.selectedObject;
    viewTab.innerHTML = `<strong>Vue du capteur n°${actualSensor.json["id"]}</strong><div id='view-object' class='container'></div>`;
}

export async function updateViewPanel() {
    if (state.selectedObject instanceof Loop)
        updateViewLoop();
    else if (state.selectedObject instanceof Switch)
        updateViewSwitch();
    else if (state.selectedObject instanceof Station)
        updateViewStation();
    else if (state.selectedObject instanceof Shed)
        updateViewShed();
    else if (state.selectedObject instanceof Pod)
        updateViewPod();
    else if (state.selectedObject instanceof Sensor)
        updateViewSensor();
}
