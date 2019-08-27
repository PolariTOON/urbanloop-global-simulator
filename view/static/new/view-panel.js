import {state} from "./state.js";
import {Switch} from "./switch.js";

const {Line, Group, Layer, Circle} = Konva;

let viewTab = document.getElementById("view-tab");
let viewObject = document.getElementById("view-object");
const notImplemented = document.createElement("strong");
notImplemented.append("Not Implemented");

const width = window.innerWidth;
const height = window.innerHeight;
const size = 150;
const sizeOut = 160;
const sizeIn = 300;
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
    container: viewObject,
    width: width,
    height: height
  });
let layer = new Layer();
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
let pod = new Circle({
  radius: 4,
  fill: 'red',
  stroke: 'black',
  strokeWidth: 1
});
let pods = [];

stage.add(layer);
layer.add(groupLines);
layer.add(groupPods);
groupLines.add(switchIn);
groupLines.add(switchOut);
groupLines.add(bridge);

function updateViewSwitch(switchInJSON, switchOutJSON, bridgeJSON) { // TODO
    console.log(switchOutJSON, switchInJSON, bridgeJSON);
    // for (const pod of pods){
    //     const pos = pod["position"];
    //     const p =
    // }
    layer.batchDraw();
}

function updateViewOther() {
    viewTab.removeChild(viewObject);
    viewTab.append(notImplemented);
}

state.addEventListener("update", (event) => {
    const networkJSON = event.detail;
    const selected = state.selectedEntity;
    let switchInJSON = null;
    let switchOutJSON = null;
    let bridgeJSON = null;
    let id_bridge = null;
    if (selected instanceof Switch){
        viewTab.removeChild(notImplemented);
        viewTab.append(viewObject);
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
    else
        updateViewOther();
});