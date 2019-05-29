import {Capsule, Loop, Station, Switch, Warehouse, appState, getNetworkDivSize} from "./objects.js";

let viewTab = document.getElementById("view-tab");

let stageView = new Konva.Stage({
    container: 'view-object',
    width: getNetworkDivSize().width, //TODO : tailles à changer
    height: getNetworkDivSize().height
});

function updateViewLoop() {
    let actualLoop = appState.selectedObject;
    viewTab.innerHTML = "<center><strong>Vue de la boucle : " + actualLoop.json["name"] + " </strong></center>";

}

function updateViewSwitch() {
    let actualSwitch = appState.selectedObject;
    viewTab.innerHTML = "<center><strong>Vue de l'aiguillage : " + actualSwitch.json["my_loop_name"] + "->" + actualSwitch.json["other_loop_name"] + "</strong></center>";
}

function updateViewStation() {
    viewTab.innerHTML = "<center><strong>Vue de la station</strong></center>";
}

function updateViewWarehouse() {
    viewTab.innerHTML = "<center><strong>Vue de l'entrepôt</strong></center>";
}

function updateViewCapsule() {
    viewTab.innerHTML = "<center><strong>Vue de la capsule</strong></center>";
}

export async function updateViewPanel() {
    if (appState.selectedObject instanceof Loop)
        updateViewLoop();
    else if (appState.selectedObject instanceof Switch)
        updateViewSwitch();
    else if (appState.selectedObject instanceof Station)
        updateViewStation();
    else if (appState.selectedObject instanceof Warehouse)
        updateViewWarehouse();
    else if (appState.selectedObject instanceof Capsule)
        updateViewCapsule();

    stageView.batchDraw();
}
