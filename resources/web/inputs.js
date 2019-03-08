const zoomIntensity = 1.1;
const minScale = 0.01;
let moveIntensity = 1;
let pressTimeout;
let doPan = false;
let running = false;
let paused = false;


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
            y: stage.y() + moveIntensity * deltaY,
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

function fitStageIntoParentContainer() {
    stage.width(networkDiv.offsetWidth);
    stage.height(networkDiv.offsetWidth);

    objects.forEach(object => {
        if (!(object instanceof Capsule)) {
            object.updatePosition();
        }
    });

    stage.batchDraw();
}

window.addEventListener('resize', fitStageIntoParentContainer);

let startButton = document.getElementById('start-button');
let stopButton = document.getElementById('stop-button');
let pauseButton = document.getElementById('pause-button');
let scaleSlider = document.getElementById('scale-slider');
backwardButton.disabled = true;
forwardButton.disabled = true;

startButton.onclick = () => {
    if (running) return;
    startButton.classList.add('not-shown');
    stopButton.classList.remove('not-shown');
    $.get('/start');
    running = true;
    backwardButton.disabled = false;
    forwardButton.disabled = false;
};

stopButton.onclick = () => {
    if (!running) return;
    stopButton.classList.add('not-shown');
    startButton.classList.remove('not-shown');
    $.get('/stop');
    running = false;
    applyNetworkScene();
    backwardButton.disabled = true;
    forwardButton.disabled = true;
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
    objects.forEach(object => object.updateScale(Math.sqrt(scaleSlider.value)));
    stage.batchDraw();
};

stage.on('mousedown', event => {
    event.evt.preventDefault();

    let shape = networkLayer.getIntersection(stage.getPointerPosition());

    if (selectedObject !== undefined && shape === null) {
        selectedObject.unselect();
    }
    generateDataPanel();
});