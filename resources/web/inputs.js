// Some elements are defined in the above file objects.js
let stopButton = document.getElementById('stop-button');
let pauseButton = document.getElementById('pause-button');
pauseButton.disabled = true;
backwardButton.disabled = true;
forwardButton.disabled = true;

const zoomIntensity = 0.9;
const minScale = 0.01;
let moveIntensity = 1;
let pressTimeout;
let doPan = false;
let running = false;
let paused = false;

function fitStageIntoParentContainer() {
    stage.width(getNetworkDivSize().width);
    stage.height(getNetworkDivSize().height);

    calibrateNetworkScene();

    objects.forEach(object => {
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
    startButton.classList.add('not-shown');
    stopButton.classList.remove('not-shown');
    $.get('/start');
    running = true;
};

stopButton.onclick = () => {
    if (!running) return;
    pauseButton.disabled = true;
    backwardButton.disabled = true;
    forwardButton.disabled = true;
    saveConfigButton.disabled = false;
    permanentConfigButton.disabled = false;
    resetConfigButton.disabled = false;
    document.getElementById('timer-span').innerHTML = "Day -<br><br>--:--:--";
    stopButton.classList.add('not-shown');
    running = false;
    $.get('/stop');
    waitingSimLoopEnd = true;
    applyNetworkScene();
};

pauseButton.onclick = () => {
    if (paused) {
        $.get('/resume');
        pauseButton.innerHTML = "Pause";
        paused = false;
        backwardButton.disabled = false;
        forwardButton.disabled = false;
    } else {
        $.get('/pause');
        pauseButton.innerHTML = "Resume";
        backwardButton.disabled = true;
        forwardButton.disabled = true;
        paused = true;
    }
};

backwardButton.onclick = () => {
    if (!running) return;
    $.get('/decelerate');
};

forwardButton.onclick = () => {
    if (!running) return;
    $.get('/accelerate');
};

scaleSlider.oninput = () => {
    $('#scale-slider').attr('data-original-title', 'Objects scale : ' + scaleSlider.value).tooltip('show');
    objectScale = scaleSlider.value;
    objects.forEach(object => object.updateScale(objectScale));
    stage.batchDraw();
};

scaleSlider.onmouseleave = () => {
    $('#scale-slider').tooltip('hide');
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

    if (selectedObject !== undefined && shape === null) {
        selectedObject.unselect();
    }
});