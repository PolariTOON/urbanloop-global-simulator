import {appState, fitStageIntoParentContainer, moveCursor, resetCursor} from "./network.js";

let scaleSlider = document.getElementById('scale-slider');
let pauseButton = document.getElementById('pause-button');
let backwardButton = document.getElementById('backward-button');
let forwardButton = document.getElementById('forward-button');

pauseButton.disabled = true;
backwardButton.disabled = true;
forwardButton.disabled = true;

const zoomIntensity = 0.9;
const minScale = 0.01;
let moveIntensity = 1;
let pressTimeout;
let doPan = false;
export let running = false;

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


//TODO : BOUTON START, STOP, PAUSE, ACCELERATE, DECELERATE


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
