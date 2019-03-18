let updateLoop;

function clearScene() {
    clearing = true;
    stopUpdateLoop();
    objects = [];
    selectedObject = undefined;
    stage.getLayers().forEach(layer => layer.destroyChildren());
    stage.destroyChildren();
}

function applyNetworkScene(networkName = String(), isDefaultNetwork = true) {
    clearScene();
    stage.add(networkLayer);
    stage.add(infoLayer);
    initNetworkScene(networkName, isDefaultNetwork);
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







