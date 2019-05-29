let updateLoop;

function clearScene() {
    clearing = true;
    stopUpdateLoop();
    objects = [];
    selectedObject = undefined;
    stage.getLayers().forEach(layer => layer.destroyChildren());
    stage.destroyChildren();
}

async function applyNetworkScene(networkName = String(), isDefaultNetwork = true) {
    clearScene();
    stage.add(networkLayer);
    stage.add(infoLayer);
    await initNetworkScene(networkName, isDefaultNetwork);
    clearing = false;
    startUpdateLoop();
}

function startUpdateLoop() {
    updateLoop = setInterval(() => {
        updateDataPanel();
        if (running) {
            updateNetworkScene();
        }
    }, 32); // 1000/32 = 31 fps
}

function stopUpdateLoop() {
    clearInterval(updateLoop);
    updateLoop = undefined;
}

(async () => {
    await applyNetworkScene();
    updateConfigPanel();
}) ();
