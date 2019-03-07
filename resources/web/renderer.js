let stage = new Konva.Stage({
    container: 'network-div',
    width: networkDiv.offsetWidth,
    height: networkDiv.offsetHeight
});

let updateLoop;
let refreshTime = 50;
networkLayer = new Konva.Layer();
infoLayer = new Konva.Layer();

function clearScene() {
    clearing = true;
    stopUpdateLoop();
    objects = [];
    selectedObject = undefined;
    stage.getLayers().forEach(layer => layer.destroyChildren());
    stage.destroyChildren();
}

function applyNetworkScene() {
    clearScene();
    stage.add(networkLayer);
    stage.add(infoLayer);
    initNetworkScene();
    clearing = false;
    startUpdateLoop();
}

function startUpdateLoop() {
    updateLoop = setInterval(() => {
        if (running) {
            updateNetworkScene();
            generateDataPanel();
        }
    }, refreshTime);
}

function stopUpdateLoop() {
    clearInterval(updateLoop);
    updateLoop = undefined;
}

applyNetworkScene();







