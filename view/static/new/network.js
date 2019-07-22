import {fetchTimeout} from "./main-page.js";
import {Loop} from "./loop.js";
import {updateStationFromJSON} from "./station.js";
import {updateShedFromJSON} from "./shed.js";
import {updateSwitchFromJSON} from "./switch.js";
import {updateSensorFromJSON} from "./sensor.js";
import {updateTimeFromJSON} from "./menu.js";
import {updatePodFromJSON} from "./pod.js";
import {updateDataPanel} from "./data-panel.js";
import {updateViewPanel} from "./view-panel.js";
import {Bridge} from "./bridge.js";
const {Group, Layer, Stage} = Konva;

const zoomIntensity = 0.8;
const minScale = 0.01;

let scaleSlider = document.getElementById('scale-slider');
let updateLoop;

export const appState = {
    clearing: false,
    objectScale: undefined,
    objects: undefined,
    selectedObject: null,
    viewBox: null,
    origin: null
};

let running = false;

const stage = new Stage({
    container: 'network-div',
    draggable: true
});
const networkLayer = new Layer();
const infoLayer = new Layer();

function scaleObjects() {
    appState.objects.forEach(object => object.updateScale(appState.objectScale));
}

function getBarycenter() {
    let loopNumber = 0;
    let sumX = 0;
    let sumY = 0;

    appState.objects.forEach(object => {
        if (object instanceof Loop) {
            loopNumber += 1;
            sumX += object.averageX;
            sumY += object.averageY;
        }
    });

    if (loopNumber === 0) {
        return {x: 0, y: 0};
    }

    return {x: sumX / loopNumber, y: sumY / loopNumber};
}

export async function initNetworkScene(network_index) {
    appState.objects = [];

    /*await fetch('/networks/0/', {
        method: "POST"
    });*/


    // On ajoute les boucles
    const loops = [];
    const bridges = [];
    const networkJSON = await (await fetch('/networks/'+ network_index +'/', {method: "GET"})).json();
    const viewBox = networkJSON["view_box"];
    const {x, y, width, height} = viewBox;
    const [offsetX, offsetY, zoom] = [0, 0, 1];
    appState.viewBox = {x, y, width, height};
    appState.origin = {offsetX, offsetY, zoom};
    for (const json of networkJSON["loops"]) {
        const loop = new Loop(json, networkLayer, infoLayer);
        loops.push(loop);
    }

    // On ajoute les ponts
    for (const json of networkJSON["bridges"]) {
        const switchIn = loops[json["switch_in"]["loop"]].elements[json["switch_in"]["element"]];
        const switchOut = loops[json["switch_out"]["loop"]].elements[json["switch_out"]["element"]];
        const bridge = new Bridge(json, switchIn, switchOut, networkJSON["loops"], networkLayer, infoLayer);
        bridges.push(bridge);
    }
    resize();

    networkLayer.batchDraw();
    infoLayer.batchDraw();
}

export async function updateNetworkScene() {
    const listDataJSON = await (await fetchTimeout(1000, '/data/')).json(); //TODO: requête data

    if (!appState.clearing) {
        for (const dataJSON of listDataJSON) {
            switch (dataJSON['jsonType']) {
                case 'time':
                    updateTimeFromJSON(dataJSON);
                    break;
                case 'station':
                    updateStationFromJSON(dataJSON);
                    break;
                case 'shed':
                    updateShedFromJSON(dataJSON);
                    break;
                case 'switch':
                    updateSwitchFromJSON(dataJSON);
                    break;
                case 'pod':
                    updatePodFromJSON(dataJSON);
                    break;
                case 'sensor':
                    updateSensorFromJSON(dataJSON);
            }
        }
    }

    networkLayer.batchDraw();
    infoLayer.batchDraw();
}

function resize() {
    const container = stage.container();
    const {offsetWidth, offsetHeight} = container;
    const {x, y, width, height} = appState.viewBox;
    const a = offsetWidth * height;
    const b = offsetHeight * width;
    let zoom = 1;
    let scaledWidth = offsetWidth;
    let scaledHeight = offsetHeight;
    if (a < b) {
        zoom = scaledWidth / width;
        scaledHeight = height * zoom;
    } else if (b < a) {
        zoom = scaledHeight / height;
        scaledWidth = width * zoom;
    }
    const offsetX = (offsetWidth - scaledWidth) / 2 - x * zoom;
    const offsetY = (offsetHeight - scaledHeight) / 2 - y * zoom;
    const ratio = zoom / appState.origin.zoom;
    const translateX = (stage.x() - appState.origin.offsetX) * ratio + offsetX;
    const translateY = (stage.y() - appState.origin.offsetY) * ratio + offsetY;
    const scaleX = stage.scaleX() * ratio;
    const scaleY = stage.scaleY() * ratio;
    appState.origin = {offsetX, offsetY, zoom};
    stage.size({
        width: offsetWidth,
        height: offsetHeight
    });
    stage.position({
        x: translateX,
        y: translateY
    });
    stage.scale({
        x: scaleX,
        y: scaleY
    });
    appState.objectScale = 1;
    scaleSlider.value = appState.objectScale;
    scaleSlider.title = "Objects scale : " + scaleSlider.value;
    scaleObjects();

    stage.batchDraw();
}

function setCursor(cursor) {
    document.body.style.cursor = cursor;
}

export function getDefaultFilename() {
    return 'new_mini_network';
}

function clearScene() {
    appState.clearing = true;
    stopUpdateLoop();
    appState.objects = [];
    appState.selectedObject = null;
    stage.getLayers().forEach(layer => layer.destroyChildren());
    stage.destroyChildren();
}

export async function applyNetworkScene(networkName = 0) {
    clearScene();
    stage.add(networkLayer);
    stage.add(infoLayer);
    await initNetworkScene(networkName);
    appState.clearing = false;
    // startUpdateLoop(); //TODO : s'arrêter ici dans un premier temps (affichage du modèle avant lancement de la simulation)
}

function startUpdateLoop() {
    updateLoop = setInterval(() => {
        updateDataPanel();
        updateViewPanel();
        if (running) {
            updateNetworkScene();
        }
    }, 32); // 1000/32 = 31 fps
}

function stopUpdateLoop() {
    clearInterval(updateLoop);
    updateLoop = undefined;
}


window.addEventListener("resize", resize);

stage.on("dragstart", (event) => {
    event.evt.preventDefault();
    setCursor("move");
});

stage.on("dragend", (event) => {
    event.evt.preventDefault();
    setCursor("auto");
});

stage.on("wheel", (event) => {
    event.evt.preventDefault();
    const ratio = zoomIntensity ** Math.sign(event.evt.deltaY);
    const ratioX = Math.max(ratio, minScale / stage.scaleX());
    const ratioY = Math.max(ratio, minScale / stage.scaleY());
    const restX = 1 - ratioX;
    const restY = 1 - ratioY;
    const translateX = stage.x() * ratioX + stage.getPointerPosition().x * restX;
    const translateY = stage.y() * ratioY + stage.getPointerPosition().y * restY;
    const scaleX = stage.scaleX() * ratioX;
    const scaleY = stage.scaleY() * ratioY;
    stage.position({
        x: translateX,
        y: translateY
    });
    stage.scale({
        x: scaleX,
        y: scaleY
    });
    stage.batchDraw();
});

stage.on("mouseover", (event) => {
    event.evt.preventDefault();
    let shape = event.target;
    while (shape !== null && !(shape instanceof Group)) {
        shape = shape.getParent();
    }
    if (shape !== null) {
        setCursor("pointer");
        shape.info.show();
    }
    infoLayer.batchDraw();
});

stage.on("mouseout", (event) => {
    event.evt.preventDefault();
    let shape = event.target;
    while (shape !== null && !(shape instanceof Group)) {
        shape = shape.getParent();
    }
    if (shape !== null) {
        setCursor("auto");
        shape.info.hide();
    }
    infoLayer.batchDraw();
});

stage.on("mousedown", (event) => {
    event.evt.preventDefault();
    let shape = event.target;
    while (shape !== null && !(shape instanceof Group)) {
        shape = shape.getParent();
    }
    if (shape === appState.selectedObject) {
        return;
    }
    if (appState.selectedObject !== null) {
        appState.selectedObject.unselect();
        appState.selectedObject = null;
    }
    if (shape !== null) {
        shape.select();
        appState.selectedObject = shape;
    }
    networkLayer.batchDraw();
});

scaleSlider.oninput = () => {
    scaleSlider.title = 'Objects scale : ' + scaleSlider.value;
    appState.objectScale = scaleSlider.value;
    appState.objects.forEach(object => object.updateScale(appState.objectScale));
    stage.batchDraw();
};

scaleSlider.onmouseleave = () => {
    scaleSlider.removeAttribute("title");
};
