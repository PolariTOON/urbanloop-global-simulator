let stage = new Konva.Stage({
    container: 'network-div',
    width: networkDiv.offsetWidth,
    height: networkDiv.offsetHeight
});

let networkLayer = new Konva.Layer();
let infoLayer = new Konva.Layer();

function clearScene() {
    if (stage.getLayer() === null) {
        return;
    }

    stage.getLayers().forEach(layer => {
        stage.remove(layer);
    });
}

function applyNetworkScene() {
    clearScene();
    stage.add(networkLayer);
    stage.add(infoLayer);
}

initNetworkScene(networkLayer, infoLayer);
applyNetworkScene(networkLayer);


setInterval(() => {
    updateNetworkScene(networkLayer, infoLayer);
}, 50);


