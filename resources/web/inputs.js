import {Capsule, appState, calibrateNetworkScene, getNetworkDivSize, moveCursor, networkLayer, resetCursor, stage} from "./objects.js";
import {changeNetworkButtonState} from "./tabs.js";
import {applyNetworkScene} from "./renderer.js";

// Some elements are defined in the above file objects.js
let scaleSlider = document.getElementById('scale-slider');
let startButton = document.getElementById('start-button');
let stopButton = document.getElementById('stop-button');
let pauseButton = document.getElementById('pause-button');
let backwardButton = document.getElementById('backward-button');
let forwardButton = document.getElementById('forward-button');
let saveConfigButton = document.getElementById('config-save-button');
let permanentConfigButton = document.getElementById('config-permanent-button');
let resetConfigButton = document.getElementById('config-reset-button');
let networkSelection = document.getElementById('conf-topology-0');
pauseButton.disabled = true;
backwardButton.disabled = true;
forwardButton.disabled = true;

const zoomIntensity = 0.9;
const minScale = 0.01;
let moveIntensity = 1;
let pressTimeout;
let doPan = false;
export let running = false;
let paused = false;

function fitStageIntoParentContainer() {
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

startButton.onclick = () => {
    if (running) return;
    pauseButton.disabled = false;
    backwardButton.disabled = false;
    forwardButton.disabled = false;
    saveConfigButton.disabled = true;
    permanentConfigButton.disabled = true;
    resetConfigButton.disabled = true;
    networkSelection.disabled = true;
    changeNetworkButtonState(true);
    startButton.classList.add('not-shown');
    stopButton.classList.remove('not-shown');
    fetch('/start');
    running = true;
};

stopButton.onclick = async () => {
    if (!running) return;
    pauseButton.disabled = true;
    backwardButton.disabled = true;
    forwardButton.disabled = true;
    saveConfigButton.disabled = false;
    permanentConfigButton.disabled = false;
    resetConfigButton.disabled = false;
    networkSelection.disabled = false;
    changeNetworkButtonState(false);
    stopButton.classList.add('not-shown');
    running = false;
    await fetch('/stop');
    document.getElementById('timer-span').innerHTML = "Day -<br><br>--:--:--";
    appState.waitingSimLoopEnd = true;
    applyNetworkScene();
};

pauseButton.onclick = () => {
    if (paused) {
        fetch('/resume');
        pauseButton.innerHTML = "Pause";
        paused = false;
    } else {
        fetch('/pause');
        pauseButton.innerHTML = "Resume";
        paused = true;
    }
};

backwardButton.onclick = () => {
    if (!running) return;
    fetch('/decelerate');
};

forwardButton.onclick = () => {
    if (!running) return;
    fetch('/accelerate');
};

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
