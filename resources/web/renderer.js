let stage = new Konva.Stage({
    container: 'network-div',
    width: networkDiv.offsetWidth,
    height: networkDiv.offsetHeight
});

networkLayer = new Konva.Layer();
infoLayer = new Konva.Layer();

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

initNetworkScene();
applyNetworkScene();

setInterval(() => {
    updateNetworkScene();
}, 50);


