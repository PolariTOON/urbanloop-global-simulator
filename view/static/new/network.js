import {Bridge} from "./bridge.js";
import {Entity} from "./entity.js";
import {Loop} from "./loop.js";
import {state} from "./state.js";
const {Group, Layer, Stage} = Konva;

const zoomIntensity = 0.8;
const minScale = 0.01;

const article = document.querySelector("main > article");
const stage = new Stage({
    container: article,
    draggable: true
});
const layer = new Layer();
stage.add(layer);
const legendsLayer = new Group();
layer.add(legendsLayer);
const elementsLayer = new Group();
layer.add(elementsLayer);
const sectionsLayer = new Group();
layer.add(sectionsLayer);
const podsLayer = new Group();
layer.add(podsLayer);
const hintsLayer = new Group();
layer.add(hintsLayer);
const heading = document.createElement("h2");
heading.textContent = "Undefined network"; // TODO
const firstParagraph = document.createElement("p");
const datetimeView = document.createElement("label");
datetimeView.innerHTML = "Date: <output>Day - ---:--:--</output></label>";
firstParagraph.append(datetimeView);
const secondParagraph = document.createElement("p");
const speedView = document.createElement("label");
speedView.innerHTML = "Speed: <output>&times;-</output></label>";
secondParagraph.append(speedView);
article.prepend(heading, firstParagraph, secondParagraph);

state.addEventListener("load", async (event) => {
    const networkJSON = event.detail;
    const viewBox = networkJSON["view_box"];
    const {x, y, width, height} = viewBox;
    const [offsetX, offsetY, zoom] = [0, 0, 1];
    state.viewBox = {x, y, width, height};
    state.origin = {offsetX, offsetY, zoom};
    const loopsJSON = networkJSON["loops"];
    const bridgesJSON = networkJSON["bridges"];
    for (const json of loopsJSON) {
        const loop = new Loop(json, legendsLayer, elementsLayer, sectionsLayer, hintsLayer);
        loop.update(json, podsLayer, hintsLayer);
        state.loops.push(loop);
    }
    for (const json of bridgesJSON) {
        const switchOut = state.loops[json["switch_out"]["loop"]]._elements[json["switch_out"]["element"]];
        const switchIn = state.loops[json["switch_in"]["loop"]]._elements[json["switch_in"]["element"]];
        const bridge = new Bridge(json, switchOut, switchIn, legendsLayer, sectionsLayer, hintsLayer);
        bridge.update(json, loopsJSON, podsLayer, hintsLayer);
        state.bridges.push(bridge);
    }
    for (const [id, pod] of state.pods.entries()) {
        pod._keepFlag = 0;
    }
    resize();
    layer.batchDraw();
});

state.addEventListener("unload", async (event) => {
    legendsLayer.destroyChildren();
    elementsLayer.destroyChildren();
    sectionsLayer.destroyChildren();
    podsLayer.destroyChildren();
    hintsLayer.destroyChildren();
    transform(0, 0, 1, 1);
    state.loops.length = 0;
    state.bridges.length = 0;
    state.nodes.length = 0;
    state.pods.clear();
    state.selectedEntity = null;
    state.viewBox = null;
    state.origin = null;
});

state.addEventListener("update", (event) => {
    const networkJSON = event.detail;
    const loopsJSON = networkJSON["loops"];
    const bridgesJSON = networkJSON["bridges"];
    for (let i = 0, li = loopsJSON.length; i < li; i++) {
        const json = loopsJSON[i];
        state.loops[i].update(json, podsLayer, hintsLayer);
    }
    for (let i = 0, li = bridgesJSON.length; i < li; i++) {
        const json = bridgesJSON[i];
        state.bridges[i].update(json, loopsJSON, podsLayer, hintsLayer);
    }
    const invertedScaleX = 1 / stage.scaleX();
    const invertedScaleY = 1 / stage.scaleY();
    for (const [id, pod] of state.pods.entries()) {
        if (pod._keepFlag === 0) {
            if (pod === state.selectedEntity) {
                state.selectedEntity = null;
            }
            pod.destroy();
            state.pods.delete(id);
        } else {
            if (pod._keepFlag === 2) {
                pod.scale({
                    x: invertedScaleX,
                    y: invertedScaleY,
                });
            }
            pod._keepFlag = 0;
        }
    }
    layer.batchDraw();
});

function resize() {
    const container = stage.container();
    const {offsetWidth, offsetHeight} = container;
    const {x, y, width, height} = state.viewBox;
    const a = offsetWidth * height;
    const b = offsetHeight * width;
    let zoom = 1;
    let scaledWidth = offsetWidth;
    let scaledHeight = offsetHeight;
    if (a < b) {
        zoom = scaledWidth / width;
        scaledHeight = height * zoom;
    } else if (b < a) {
        zoom = scaledHeight / height;
        scaledWidth = width * zoom;
    }
    const offsetX = (offsetWidth - scaledWidth) / 2 - x * zoom;
    const offsetY = (offsetHeight - scaledHeight) / 2 - y * zoom;
    const ratio = zoom / state.origin.zoom;
    const translateX = (stage.x() - state.origin.offsetX) * ratio + offsetX;
    const translateY = (stage.y() - state.origin.offsetY) * ratio + offsetY;
    const scaleX = stage.scaleX() * ratio;
    const scaleY = stage.scaleY() * ratio;
    state.origin = {offsetX, offsetY, zoom};
    stage.size({
        width: offsetWidth,
        height: offsetHeight,
    });
    transform(translateX, translateY, scaleX, scaleY);
}

function zoom(delta) {
    const ratio = zoomIntensity ** Math.sign(delta);
    const ratioX = Math.max(ratio, minScale / stage.scaleX());
    const ratioY = Math.max(ratio, minScale / stage.scaleY());
    const restX = 1 - ratioX;
    const restY = 1 - ratioY;
    const translateX = stage.x() * ratioX + stage.getPointerPosition().x * restX;
    const translateY = stage.y() * ratioY + stage.getPointerPosition().y * restY;
    const scaleX = stage.scaleX() * ratioX;
    const scaleY = stage.scaleY() * ratioY;
    transform(translateX, translateY, scaleX, scaleY);
}

function transform(translateX, translateY, scaleX, scaleY) {
    stage.position({
        x: translateX,
        y: translateY,
    });
    stage.scale({
        x: scaleX,
        y: scaleY,
    });
    const invertedScaleX = 1 / scaleX;
    const invertedScaleY = 1 / scaleY;
    for (const entity of [...state.loops, ...state.bridges, ...state.nodes, ...state.pods.values()]) {
        entity.scale({
            x: invertedScaleX,
            y: invertedScaleY,
        });
    }
}

function setCursor(cursor) {
    document.documentElement.style.cursor = cursor;
}

window.addEventListener("resize", async (event) => {
    event.preventDefault();
    resize();
    layer.batchDraw();
});

stage.on("dragstart", async (event) => {
    event.evt.preventDefault();
    setCursor("move");
});

stage.on("dragend", async (event) => {
    event.evt.preventDefault();
    setCursor("auto");
});

stage.on("wheel", async (event) => {
    event.evt.preventDefault();
    zoom(event.evt.deltaY);
    layer.batchDraw();
});

stage.on("mouseover", async (event) => {
    event.evt.preventDefault();
    let shape = event.target;
    while (shape !== null && !(shape instanceof Entity)) {
        shape = shape.getParent();
    }
    if (shape === null || shape === state.selectedEntity) {
        return;
    }
    shape.showHint();
    layer.batchDraw();
    setCursor("pointer");
});

stage.on("mouseout", async (event) => {
    event.evt.preventDefault();
    let shape = event.target;
    while (shape !== null && !(shape instanceof Entity)) {
        shape = shape.getParent();
    }
    if (shape === null || shape === state.selectedEntity) {
        return;
    }
    shape.hideHint();
    layer.batchDraw();
    setCursor("auto");
});

stage.on("click", async (event) => {
    event.evt.preventDefault();
    let shape = event.target;
    while (shape !== null && !(shape instanceof Entity)) {
        shape = shape.getParent();
    }
    if (shape === state.selectedEntity) {
        return;
    }
    if (state.selectedEntity !== null) {
        state.selectedEntity.hideHint();
        state.selectedEntity.unselect();
        state.selectedEntity = null;
    }
    if (shape !== null) {
        shape.showHint();
        shape.select();
        state.selectedEntity = shape;
    }
    layer.batchDraw();
    setCursor("auto");
});
