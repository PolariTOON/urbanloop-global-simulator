import {appState, infoLayer, initNetworkScene, networkLayer, stage, updateNetworkScene} from "./objects.js";
import {updateDataPanel} from "./tabs.js";
import {running} from "./inputs.js";

let updateLoop;

function clearScene() {
    appState.clearing = true;
    stopUpdateLoop();
    appState.objects = [];
    appState.selectedObject = undefined;
    stage.getLayers().forEach(layer => layer.destroyChildren());
    stage.destroyChildren();
}

export async function applyNetworkScene(networkName = String(), isDefaultNetwork = true) {
    clearScene();
    stage.add(networkLayer);
    stage.add(infoLayer);
    await initNetworkScene(networkName, isDefaultNetwork);
    appState.clearing = false;
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
