import {running} from "./inputs";

let networkDiv = document.getElementById('network-div');
let scaleSlider = document.getElementById('scale-slider');

export const appState = {
    clearing: false,
    objectScale: undefined,
    objects: undefined,
    selectedObject: undefined
};
let networkSize = 1000;
export let stage = new Konva.Stage({
    container: 'network-div',
    width: getNetworkDivSize().width,
    height: getNetworkDivSize().height
});
export let networkLayer = new Konva.Layer();
export let infoLayer = new Konva.Layer();
let updateLoop;

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
            sumX += object.json['x'];
            sumY += getNetworkDivSize().height - object.json['y'];
        }
    });

    if (loopNumber === 0) {
        return {x: 0, y: 0};
    }

    return {x: sumX / loopNumber, y: sumY / loopNumber};
}

export async function initNetworkScene() {
    appState.objects = [];
    startButton.classList.remove('not-shown');

    calibrateNetworkScene();

    networkLayer.batchDraw();
    infoLayer.batchDraw();
}

export async function updateNetworkScene() {
    const listDataJSON = await (await fetchTimeout(1000, '/networks/0/')).json(); //TODO : gestion de plusieurs simulations

    if (!appState.clearing) {
        for (const dataJSON of listDataJSON) {
            switch (dataJSON['jsonType']) {
                case 'time':
                    updateTimeFromJSON(dataJSON);
                    break;
                case 'station':
                    updateStationFromJSON(dataJSON);
                    break;
                case 'warehouse':
                    updateWarehouseFromJSON(dataJSON);
                    break;
                case 'switch':
                    updateSwitchFromJSON(dataJSON);
                    break;
                case 'capsule':
                    updateCapsuleFromJSON(dataJSON);
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
        if (!(object instanceof Capsule)) {
            object.updatePosition();
        }
    });

    stage.batchDraw();
}

export function initBehaviors(object, innerShape, outerShape, info = undefined) {
    const hasInfo = info !== undefined;

    innerShape.on('mousedown', () => {
        object.select();
    });

    outerShape.on('mousedown', () => {
        object.select();
    });

    innerShape.on('mouseover', () => {
        handCursor();
        if (hasInfo) {
            info.show();
            infoLayer.batchDraw();
        }
    });

    outerShape.on('mouseover', () => {
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

    outerShape.on('mouseout', () => {
        moveCursor();
        if (hasInfo) {
            info.hide();
            infoLayer.batchDraw();
        }
    });
}

function handCursor() {
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

export async function applyNetworkScene(networkName = getDefaultFilename()) {
    clearScene();
    stage.add(networkLayer);
    stage.add(infoLayer);
    await initNetworkScene(networkName);
    appState.clearing = false;
    startUpdateLoop();
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
