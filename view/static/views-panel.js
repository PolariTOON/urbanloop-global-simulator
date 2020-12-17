import {state} from "./state.js";
import {Switch} from "./switch.js";
import {Station} from "./station.js";

const {Line, Group, Layer, Circle} = Konva;

const viewsTab = document.getElementById("views-content");
const viewsObject = document.createElement("div");
const notImplemented = document.createElement("p");
notImplemented.append("Not implemented");

const width = 360; // largeur du canvas
const height = 200; // hauteur du canvas
const size = 150; // hauteur de l'aiguillage = distance C1C2
const sizeOut = 160; // longueur de la ligne du switchOut
const sizeIn = 300; // longueur de la ligne du switchIn
const margin = 30;
const xC1 = margin;
const yC1 = margin;
const xC2 = margin;
const yC2 = size;
const xM1 = margin + sizeOut;
const yM1 = margin;
const xM2 = margin + sizeIn;
const yM2 = size;

let stage = new Konva.Stage({
  container: viewsObject,
  width: width,
  height: height
});
let layerSwitch = new Layer();
let groupLines = new Group();
let groupPods = new Group();
let switchOut = new Line({
  x: 0,
  y: 0,
  points: [xC1, yC1, xM1, yM1],
  stroke: 'black',
  strokeWidth: 3
});
let switchIn = new Line({
  x: 0,
  y: 0,
  points: [xC2, yC2, xM2, yM2],
  stroke: 'black',
  strokeWidth: 3
});
let bridge = new Line({
  x: 0,
  y: 0,
  points: [xM1, yM1, xM2, yM2],
  stroke: 'black',
  strokeWidth: 3
});
let podsOut = [];
let podsIn = [];
let podsBridge = [];

stage.add(layerSwitch);
layerSwitch.add(groupLines);
layerSwitch.add(groupPods);
groupLines.add(switchIn);
groupLines.add(switchOut);
groupLines.add(bridge);

const firstPlaceX = 40;
const firstPlaceY = 40;
const radius = 20;
const travelLength = 100;

let layerStation = new Layer();
const line1 = new Line({
    x: 0,
    y: 0,
    points: [firstPlaceX - radius*1.25, firstPlaceY-radius, firstPlaceX - radius*1.25, firstPlaceY+radius],
    stroke: 'black',
    strokeWidth: 2
});
const line2 = new Line({
    x: 0,
    y: 0,
    points: [firstPlaceX + radius*1.25, firstPlaceY-radius, firstPlaceX + radius*1.25, firstPlaceY+radius],
    stroke: 'black',
    strokeWidth: 2
});
const line3 = new Line({
    x: 0,
    y: 0,
    points: [firstPlaceX + radius*3.75, firstPlaceY-radius, firstPlaceX + radius*3.75, firstPlaceY+radius],
    stroke: 'black',
    strokeWidth: 2
});
const line4 = new Line({
    x: 0,
    y: 0,
    points: [firstPlaceX + radius*6.25, firstPlaceY-radius, firstPlaceX + radius*6.25, firstPlaceY+radius],
    stroke: 'black',
    strokeWidth: 2
});
const line5 = new Line({
    x: 0,
    y: 0,
    points: [firstPlaceX + radius*8.75, firstPlaceY-radius, firstPlaceX + radius*8.75, firstPlaceY+radius],
    stroke: 'black',
    strokeWidth: 2
});

stage.add(layerStation);
layerStation.add(line1);
layerStation.add(line2);
layerStation.add(line3);
layerStation.add(line4);
layerStation.add(line5);

let podsStation = [null, null, null, null];
let boarding = [false, false, false, false];
let travelers = [null, null, null, null];
let previous = [null, null, null, null];
let ratio = [1, 1, 1, 1];

layerSwitch.hide();
layerStation.hide();

function getPodFromName(list, name){
    for (const e of list){
        if (e["name"] === name)
            return e["pod"];
    }
    return null;
}

function removeExtraPods(pods, newPods){
    for (const dicoPod of pods){
        const p = getPodFromName(newPods, dicoPod["name"]);
        if (p === null){
            dicoPod["pod"].destroy();
        }
    }
}

function updatePodsSwitch(jsonFile, pods){
    const length = jsonFile["length"];
    let x = 0;
    let y = 0;
    let newPods = [];
    for (const pod of jsonFile["pods"]){
        const pos = pod["position"];
        if (jsonFile["type"] === "switch_out"){
            x = margin + pos * sizeOut / length;
            y = margin;
        } else {
            x = margin + pos * sizeIn / length;
            y = size;
        }
        const p = getPodFromName(pods, pod["name"]);
        if (p === null){
            const newPod = new Circle({
              x: x,
              y: y,
              radius: 4,
              fill: 'red',
              stroke: 'black',
              strokeWidth: 1
            });
            groupPods.add(newPod);
            newPods.push({"name": pod["name"], "pod": newPod});
        } else {
            p.x(x);
            p.y(y);
            newPods.push({"name": pod["name"], "pod": p})
        }
    }
    removeExtraPods(pods, newPods);
    if (jsonFile["type"] === "switch_out"){
            podsOut = newPods;
        } else {
            podsIn = newPods;
        }
}

function updatePodsBridge(jsonFile, pods) {
    const length = jsonFile["sections"][0]["length"];
    let newPods = [];
    for (const pod of jsonFile["pods"]){
        const pos = pod["position"];
        const ratio = pos / length;
        const x = xM1 + (xM2 - xM1) * ratio;
        const y = yM1 + (yM2 - yM1) * ratio;
        const p = getPodFromName(pods, pod["name"]);
        if (p === null){
            const newPod = new Circle({
          x: x,
          y: y,
          radius: 4,
          fill: 'red',
          stroke: 'black',
          strokeWidth: 1
        });
            groupPods.add(newPod);
            newPods.push({"name": pod["name"], "pod": newPod});
        } else {
            p.x(x);
            p.y(y);
            newPods.push({"name": pod["name"], "pod": p})
        }
    }
    removeExtraPods(pods, newPods);
    podsBridge = newPods
}

function updateViewSwitch(switchInJSON, switchOutJSON, bridgeJSON) {
    updatePodsSwitch(switchOutJSON, podsOut);
    updatePodsBridge(bridgeJSON, podsBridge);
    updatePodsSwitch(switchInJSON, podsIn);
    layerSwitch.batchDraw();
}

function updateViewOther() {
    viewsObject.remove();
    viewsTab.append(notImplemented);
}

state.addEventListener("update", (event) => {
    const networkJSON = event.detail;
    const selected = state.selectedEntity;
    let switchInJSON = null;
    let switchOutJSON = null;
    let bridgeJSON = null;
    let id_bridge = null;
    if (selected instanceof Switch){
        notImplemented.remove();
        layerStation.hide();
        layerSwitch.show();
        viewsTab.append(viewsObject);
        b1: for (const loop of networkJSON["loops"]){
            for (const elt of loop["elements"]){
                if (selected._name === elt["name"]){
                    id_bridge = elt["id_bridge"];
                    if (elt["type"] === "switch_in")
                        switchInJSON = elt;
                    else
                        switchOutJSON = elt;
                    break b1;
                }
            }
        }
        bridgeJSON = networkJSON["bridges"][id_bridge];
        b2: for (const loop of networkJSON["loops"]){
            for (const elt of loop["elements"]){
                if (selected._name !== elt["name"] && elt["id_bridge"] === id_bridge){
                    if (elt["type"] === "switch_in")
                        switchInJSON = elt;
                    else
                        switchOutJSON = elt;
                    break b2;
                }
            }
        }
        updateViewSwitch(switchInJSON, switchOutJSON, bridgeJSON);
    }
    else if (selected instanceof Station) {
      notImplemented.remove();
      viewsTab.append(viewsObject);
      layerSwitch.hide();
      layerStation.show();
      for (const loop of networkJSON["loops"]) {
        for (const elt of loop["elements"]) {
          if (selected._name === elt["name"]) {
            for (let i = selected._podMax; i < 10; i++) {
                if (podsStation[i]){
                    podsStation[i]["outer"].destroy();
                    podsStation[i]["inner"].destroy();
                    podsStation[i] = null;
                }
                if (travelers[i]){
                    travelers[i].remove()
                }
            }
            for (let i = 0; i < selected._podMax; i++) {
              if (selected._podPos[i]) {  // affichage des pods vides ou pleins de la station
                if (podsStation[i] == null) {
                  const outerShape = new Circle({
                    x: firstPlaceX + i * radius * 2.5,
                    y: firstPlaceY,
                    radius: radius,
                    fill: 'yellow',
                    stroke: 'black',
                    strokeWidth: 1
                  });
                  const innerShape = new Circle({
                    x: firstPlaceX + i * radius * 2.5,
                    y: firstPlaceY,
                    radius: radius * 0.75,
                    fill: 'white',
                    stroke: 'black',
                    strokeWidth: 1
                  });
                  podsStation[i] = {
                    outer: outerShape,
                    inner: innerShape
                  };
                  layerStation.add(outerShape);
                  layerStation.add(innerShape);
                  if (travelers[i] != null) {
                      travelers[i] = null
                  }
                } else if (selected._podFull[i] && !selected._podBoarding[i]) {
                  podsStation[i]["inner"].fill('black');
                } else {
                  podsStation[i]["inner"].fill('white');
                }

                if (selected._podBoarding[i]) {
                  if (travelers[i] == null) {
                      const traveler = new Circle({     // points des passagers en embarquement
                          x: firstPlaceX + i * radius * 2.5,
                          y: firstPlaceY + radius + travelLength,
                          radius: 5,
                          fill: 'black',
                          stroke: 'black',
                          strokeWidth: 1
                      });
                      travelers[i] = traveler;
                      layerStation.add(traveler);
                      previous[i] = Date.now();
                  } else {
                    const now = Date.now();
                    const dist = (now - previous[i]) * travelLength / selected._travelerBoardingTimes[i] / 1000;
                    travelers[i].y(travelers[i].y() - dist);
                    previous[i] = now;
                  }
                } else if (travelers[i] != null) {
                    travelers[i].remove();
                    travelers[i]= null;
                }
              } else {
                if (podsStation[i] != null) {
                  podsStation[i]["outer"].destroy();
                  podsStation[i]["inner"].destroy();
                  podsStation[i] = null;
                  if (travelers[i] != null){
                      travelers[i].remove();
                  }
                }
              }
            }
          }
        }
      }
      layerStation.batchDraw();
    }
    else
        updateViewOther();
});
