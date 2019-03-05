const zoomIntensity = 1.1;
const minScale = 0.5;
let moveIntensity = 1;
let pressTimeout;
let doPan = false;


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
    stage.draw();
}

window.addEventListener('resize', fitStageIntoParentContainer);

// buttons
let startButton = document.getElementById('start-button');
let stopButton = document.getElementById('stop-button');
let pauseButton = document.getElementById('pause-button');
let backwardButton = document.getElementById('backward-button');
let forwardButton = document.getElementById('forward-button');

/*
 *  0 : not running
 *  1 : running
 *  2 : paused
*/
let state = 0;

startButton.onclick = () => {
    startButton.classList.add('not-shown');
    stopButton.classList.remove('not-shown');
    $.get('/start');
    state = 1;
};

stopButton.onclick = () => {
    stopButton.classList.add('not-shown');
    startButton.classList.remove('not-shown');
    // $.get('/stop');
    state = 0;
};

pauseButton.onclick = () => {
    if (state === 0)
        return;
    if (state === 1) {
        // $.get('/pause');
        state = 2;
    } else {
        // $.get('/resume');
        state = 1;
    }
}

backwardButton.onclick = () => {
    // TODO
}

forwardButton.onclick = () => {
    // TODO
}

stage.on('mousedown', event => {
    event.evt.preventDefault();

    let shape = networkLayer.getIntersection(stage.getPointerPosition());

    if (selectedObject !== undefined && shape === null) {
        selectedObject.unselect();
    }
    generateDataPanel();
});