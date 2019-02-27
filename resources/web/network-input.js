let zoomIntensity = 0.1;
let minScale = 0.5;
let moveIntensity = 0.5;
let pressTimeout;
let doPan = false;

networkDiv.onwheel = function (event) {
    event.preventDefault();
    zoom(event);
};

networkDiv.onmousedown = function (event) {
    event.preventDefault();
    pressTimeout = setTimeout(function () {
        doPan = true;
    }, 200);
};

networkDiv.onmouseup = function (event) {
    event.preventDefault();
    if (pressTimeout !== null) {
        clearTimeout(pressTimeout);
        pressTimeout = null;
    }
    doPan = false;
};

networkDiv.onmousemove = function (event) {
    event.preventDefault();
    if (doPan) {
        pan(event);
    }
};


function pan(mouseEvent) {
    let deltaX = mouseEvent.movementX || mouseEvent.mozMovementX || mouseEvent.webkitMovementX || 0;
    let deltaY = mouseEvent.movementY || mouseEvent.mozMovementY || mouseEvent.webkitMovementY || 0;

    app.stage.x -= moveIntensity * deltaX;
    app.stage.y -= moveIntensity * deltaY;
}


function zoom(mouseEvent) {
    let sign = mouseEvent.deltaY < 0 ? 1 : -1;
    let zoomValue = sign * zoomIntensity;

    app.stage.scale.x = Math.max(minScale, app.stage.scale.x + zoomValue);
    app.stage.scale.y = Math.max(minScale, app.stage.scale.y + zoomValue);
}