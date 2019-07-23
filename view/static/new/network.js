import {Bridge} from "./bridge.js";
import {Entity} from "./entity.js";
import {updateDataPanel} from "./data-panel.js";
import {Loop} from "./loop.js";
import {updateViewPanel} from "./view-panel.js";
const {Layer, Stage} = Konva;

const zoomIntensity = 0.8;
const minScale = 0.01;

let updateLoop;

export const appState = {
    clearing: false,
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
    transform(translateX, translateY, scaleX, scaleY);
}

function zoom(delta) {
    const ratio = zoomIntensity ** Math.sign(delta);
    const ratioX = Math.max(ratio, minScale / stage.scaleX());
    const ratioY = Math.max(ratio, minScale / stage.scaleY());
    const restX = 1 - ratioX;
    const restY = 1 - ratioY;
    const translateX = stage.x() * ratioX + stage.getPointerPosition().x * restX;
    const translateY = stage.y() * ratioY + stage.getPointerPosition().y * restY;
    const scaleX = stage.scaleX() * ratioX;
    const scaleY = stage.scaleY() * ratioY;
    transform(translateX, translateY, scaleX, scaleY);
}

function transform(translateX, translateY, scaleX, scaleY) {
    stage.position({
        x: translateX,
        y: translateY,
    });
    stage.scale({
        x: scaleX,
        y: scaleY,
    });
    const invertedScaleX = 1 / scaleX;
    const invertedScaleY = 1 / scaleY;
    for (const object of appState.objects) {
        object.scale({
            x: invertedScaleX,
            y: invertedScaleY,
        });
    }
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

window.addEventListener("resize", (event) => {
    event.preventDefault();
    resize();
    networkLayer.batchDraw();
    infoLayer.batchDraw();
});

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
    zoom(event.evt.deltaY);
    networkLayer.batchDraw();
    infoLayer.batchDraw();
});

stage.on("mouseover", (event) => {
    event.evt.preventDefault();
    let shape = event.target;
    while (shape !== null && !(shape instanceof Entity)) {
        shape = shape.getParent();
    }
    if (shape === null) {
        return;
    }
    setCursor("pointer");
    if (shape !== appState.selectedObject) {
        shape.showHint();
        infoLayer.batchDraw();
    }
});

stage.on("mouseout", (event) => {
    event.evt.preventDefault();
    let shape = event.target;
    while (shape !== null && !(shape instanceof Entity)) {
        shape = shape.getParent();
    }
    if (shape === null) {
        return;
    }
    setCursor("auto");
    if (shape !== appState.selectedObject) {
        shape.hideHint();
        infoLayer.batchDraw();
    }
});

stage.on("mousedown", (event) => {
    event.evt.preventDefault();
    let shape = event.target;
    while (shape !== null && !(shape instanceof Entity)) {
        shape = shape.getParent();
    }
    if (shape === appState.selectedObject) {
        return;
    }
    if (appState.selectedObject !== null) {
        appState.selectedObject.hideHint();
        appState.selectedObject.unselect();
        appState.selectedObject = null;
    }
    if (shape !== null) {
        shape.showHint();
        shape.select();
        appState.selectedObject = shape;
    }
    networkLayer.batchDraw();
    infoLayer.batchDraw();
});
