import {fetchTimeout} from "./main-page.js";
import {Loop} from "./loop.js";
import {updateStationFromJSON} from "./station.js";
import {updateShedFromJSON} from "./shed.js";
import {updateSwitchFromJSON} from "./switch.js";
import {updateSensorFromJSON} from "./sensor.js";
import {updateTimeFromJSON} from "./menu.js";
import {updatePodFromJSON, Pod} from "./pod.js";
import {updateDataPanel} from "./data-panel.js";
import {updateViewPanel} from "./view-panel.js";
import {Bridge} from "./bridge.js";

const zoomIntensity = 0.8;
const minScale = 0.01;

let moveIntensity = 1;
let pressTimeout;
let doPan = false;
let networkDiv = document.getElementById('network-div');
let scaleSlider = document.getElementById('scale-slider');
let startButton = document.getElementById('start-button');
let networkSize = 1000;
let updateLoop;

export const appState = {
    clearing: false,
    objectScale: undefined,
    objects: undefined,
    selectedObject: undefined
};

export let running = false;

export let stage = new Konva.Stage({
    container: 'network-div',
    width: getNetworkDivSize().width,
    height: getNetworkDivSize().height
});
export let networkLayer = new Konva.Layer();
export let infoLayer = new Konva.Layer();

export function getNetworkDivSize() {
    return {
        width: Math.min(networkDiv.offsetWidth, window.innerWidth),
        height: Math.min(networkDiv.offsetHeight, window.innerHeight)
    }
}

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
            sumY += getNetworkDivSize().height - object.averageY;
        }
    });

    if (loopNumber === 0) {
        return {x: 0, y: 0};
    }

    return {x: sumX / loopNumber, y: sumY / loopNumber};
}

export async function initNetworkScene(network_index) {
    appState.objects = [];
    startButton.classList.remove('not-shown');

    /*await fetch('/networks/0/load/', {
        method: "POST"
    });

    const networkJSON = await (await fetch('/networks/0/', { //TODO: requête networks load
        method: "GET"
    })).json();*/

    // On ajoute les boucles
    let loops = [];
    const networkJSON = await (await fetch('/networks/'+ network_index +'/', {method: "GET"})).json();
    const viewBox = networkJSON["view_box"];
    networkSize = Math.max(viewBox["width"], viewBox["height"])*1.05;
    for (const loop of networkJSON["loops"]){
        const l = new Loop(loop);
        loops.push(l);
    }

    // On ajoute les ponts
    for (const bridge of networkJSON["bridges"]){
        const switchIn = loops[bridge["switch_in"]["loop"]].elements[bridge["switch_in"]["element"]];
        const switchOut = loops[bridge["switch_out"]["loop"]].elements[bridge["switch_out"]["element"]];
        new Bridge(bridge, switchIn, switchOut, networkJSON["loops"]);
    }

    calibrateNetworkScene();

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

export function calibrateNetworkScene() {
    calibrateStageScale();
    appState.objectScale = Math.min(networkSize / getNetworkDivSize().height, scaleSlider.max);
    scaleSlider.value = appState.objectScale;
    scaleSlider.title = "Objects scale : " + scaleSlider.value;
    calibrateStagePosition();
    scaleObjects();
}

function calibrateStagePosition() {
    if (appState.objectScale === 0) return;
    const barycenter = getBarycenter();
    const scale = networkSize / Math.min(getNetworkDivSize().width, getNetworkDivSize().height);
    const stagePos = {
        x: -barycenter.x / scale + getNetworkDivSize().width / 2,
        y: -barycenter.y / scale + getNetworkDivSize().height / 2
    };
    stage.position(stagePos);
}

function calibrateStageScale() {
    const stageScale = Math.min(getNetworkDivSize().width, getNetworkDivSize().height) / networkSize;
    stage.scale({x: stageScale, y: stageScale});
}

export function fitStageIntoParentContainer() {
    stage.width(getNetworkDivSize().width);
    stage.height(getNetworkDivSize().height);

    calibrateNetworkScene();

    appState.objects.forEach(object => {
        if (!(object instanceof Pod)) {
            object.updatePosition();
        }
    });

    stage.batchDraw();
}

export function initBehaviors(object, innerShape, outerShape = undefined, info = undefined) {
    const hasInfo = info !== undefined;

    if (outerShape){
        outerShape.on('mousedown', () => {
        object.select();
        });

        outerShape.on('mouseover', () => {
        handCursor();
        if (hasInfo) {
            info.show();
            infoLayer.batchDraw();
        }
        });

        outerShape.on('mouseout', () => {
        moveCursor();
        if (hasInfo) {
            info.hide();
            infoLayer.batchDraw();
        }
        });
    }

    innerShape.on('mousedown', () => {
        object.select();
    });

    innerShape.on('mouseover', () => {
        handCursor();
        if (hasInfo) {
            info.show();
            infoLayer.batchDraw();
        }
    });

    innerShape.on('mouseout', () => {
        moveCursor();
        if (hasInfo) {
            info.hide();
            infoLayer.batchDraw();
        }
    });
}

export function handCursor() {
    document.body.style.cursor = 'pointer';
}

export function moveCursor() {
    document.body.style.cursor = 'move';
}

export function resetCursor() {
    document.body.style.cursor = 'auto';
}

export function getDefaultFilename() {
    return 'new_mini_network';
}

function clearScene() {
    appState.clearing = true;
    stopUpdateLoop();
    appState.objects = [];
    appState.selectedObject = undefined;
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


window.addEventListener('resize', fitStageIntoParentContainer);

stage.on('mousedown', event => {
    event.evt.preventDefault();
    pressTimeout = setTimeout(function () {
        doPan = true;
    }, 100);
});

stage.on('mouseup', event => {
    event.evt.preventDefault();
    if (pressTimeout !== null) {
        clearTimeout(pressTimeout);
        pressTimeout = null;
    }
    doPan = false;
});

stage.on('mousemove', event => {
    event.evt.preventDefault();
    if (doPan) {
        let deltaX = event.evt.movementX || 0;
        let deltaY = event.evt.movementY || 0;

        let newPos = {
            x: stage.x() + moveIntensity * deltaX,
            y: stage.y() + moveIntensity * deltaY
        };

        stage.position(newPos);
        stage.batchDraw();
    }
});

stage.on('wheel', event => {
    event.evt.preventDefault();
    let oldScale = stage.scaleX();

    let mousePointTo = {
        x: stage.getPointerPosition().x / oldScale - stage.x() / oldScale,
        y: stage.getPointerPosition().y / oldScale - stage.y() / oldScale
    };

    let newScale =
        event.evt.deltaY > 0 ? oldScale * zoomIntensity : oldScale / zoomIntensity;

    if (newScale < minScale) {
        return;
    }

    stage.scale({x: newScale, y: newScale});

    let newPos = {
        x: -(mousePointTo.x - stage.getPointerPosition().x / newScale) * newScale,
        y: -(mousePointTo.y - stage.getPointerPosition().y / newScale) * newScale
    };

    stage.position(newPos);
    stage.batchDraw();
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

document.getElementById('panel-div').onmouseenter = () => {
    resetCursor();
};

stage.on('mouseover', event => {
    event.evt.preventDefault();

    if (networkLayer.getIntersection(stage.getPointerPosition()) === null) {
        moveCursor();
    }
});

stage.on('mousedown', event => {
    event.evt.preventDefault();

    let shape = networkLayer.getIntersection(stage.getPointerPosition());

    if (appState.selectedObject !== undefined && shape === null) {
        appState.selectedObject.unselect();
    }
});
