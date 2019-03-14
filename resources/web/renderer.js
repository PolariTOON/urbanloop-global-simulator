stage = new Konva.Stage({
    container: 'network-div',
    width: getNetworkDivSize().width,
    height: getNetworkDivSize().height
});
networkLayer = new Konva.Layer();
infoLayer = new Konva.Layer();
let updateLoop;

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
        updateDataPanel();
        if (running) {
            updateNetworkScene();
        }
    }, 30);
}

function stopUpdateLoop() {
    clearInterval(updateLoop);
    updateLoop = undefined;
}

applyNetworkScene();
updateConfigPanel();







