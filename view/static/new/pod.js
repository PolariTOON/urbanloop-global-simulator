import {appState, networkLayer, getNetworkDivSize, initBehaviors} from "./network.js";

export const defaultPodWidth = 5;
const podInnerEmptyColor = 'rgb(173, 72, 45)';
const podOuterEmptyColor = 'rgb(255, 100, 63)';
const podInnerAboardColor = 'rgb(96, 167, 27)';
const podOuterAboardColor = 'rgb(128, 214, 30)';
const podInnerSelectedColor = 'rgb(255, 200, 20)';
const podOuterSelectedColor = 'rgb(255, 234, 87)';

function distanceBetween(beginElement, endElement, path) {
    let d = 0;
    switch (path["type"]) {
        case "line":
        default:
            d = Math.sqrt((beginElement["x"] - endElement["x"])**2 + (beginElement["y"] - endElement["y"])**2);
    }
    return d;
}

function xyFromPosition(podJSON, loopJSON){
    const loopSize = loopJSON["elements"].length;
    let d = 0;
    let index = 0;
    let distanceToNext = 0;
    while (d < podJSON["position"]){
        const beginElement = loopJSON["elements"][index];
        const endElement = loopJSON["elements"][(index+1)%loopSize];
        const path = loopJSON["sections"][index]["path"];
        distanceToNext = distanceBetween(beginElement, endElement, path);
        if (d + distanceToNext < podJSON["position"]){
            d += distanceToNext;
            ++index;
        }
        else
            break;
    }
    d = podJSON["position"] - d;
    const beginElement = loopJSON["elements"][index];
    const endElement = loopJSON["elements"][(index+1)%loopSize];
    const D = distanceBetween(beginElement, endElement, loopJSON["sections"][index]["path"]);
    let xy = [loopJSON["elements"][index]["x"], loopJSON["elements"][index]["y"]];
    switch (loopJSON["sections"][index]["path"]["type"]){
        case "line":
        default:
            const coeff = d / D;
            xy[0] = coeff * (beginElement["x"] + endElement["x"]);
            xy[1] = coeff * (beginElement["y"] + endElement["y"]);
    }
    return xy;
}

export class Pod {
    constructor(podJSON, loopJSON, isDocked, podWidth = defaultPodWidth) {
        this.json = podJSON;
        this.id = podJSON["name"];
        this.travelerNumber = podJSON["travelers"]["count"];
        this.isDocked = isDocked;
        const xy = xyFromPosition(podJSON, loopJSON);
        this.x = xy[0];
        this.y = xy[1];


        this.innerCircle = new Konva.Circle({
            x: this.x,
            y: this.y,
            name: this.id,
            radius: podWidth - Math.sqrt(podWidth),
        });

        this.outerCircle = new Konva.Circle({
            x: this.x,
            y: this.y,
            name: this.id,
            radius: podWidth,
        });

        initBehaviors(this, this.innerCircle, this.outerCircle);

        networkLayer.add(this.outerCircle);
        networkLayer.add(this.innerCircle);
        //this.update(podJSON);
        this.updateColor()
        appState.objects.push(this);
    }

    select() {
        if (appState.selectedObject !== undefined && appState.selectedObject !== this) {
            appState.selectedObject.unselect();
        }

        appState.selectedObject = this;
        this.innerCircle.fill(podInnerSelectedColor);
        this.outerCircle.fill(podOuterSelectedColor);
        networkLayer.batchDraw();
    }

    unselect() {
        if (appState.selectedObject === this) {
            appState.selectedObject = undefined;
        }

        this.updateColor();
        networkLayer.batchDraw();
    }

    update(podJSON) {
        /*this.isDocked = !podJSON['moving'];
        this.travelerNumber = podJSON["travelers"]["count"];*/
        this.json = podJSON;
        //this.track = podJSON['currentElementUuid']; TODO: à gérer

        /*if (this.isDocked) {
            if (podJSON['stationIndex'] === -1) { // THIS IS HOTFIX FOR GHOST CAPS
                this.innerCircle.hide();
                this.outerCircle.hide();
                return;
            }
            let targetStations = appState.objects.filter(station => station.uuid.includes(podJSON['currentElementUuid']));
            targetStations.forEach(station => {
                this.innerCircle.x(x + 10 * station.stationRadius + (6 * podJSON['stationIndex'] + 2) * station.dockSize);
                this.outerCircle.x(x + 10 * station.stationRadius + (6 * podJSON['stationIndex'] + 2) * station.dockSize);
            });
        }*/

        this.updateColor();
    }

    updateColor() {
        if (appState.selectedObject === this) {
            return;
        }

        if (this.isDocked) {
            if (appState.selectedObject === undefined || this.currentElementUuid !== appState.selectedObject.uuid) {
                this.innerCircle.hide();
                this.outerCircle.hide();
            } else {
                this.innerCircle.show();
                this.outerCircle.show();
            }
        } else {
            this.innerCircle.show();
            this.outerCircle.show();
        }

        if (this.isAboard()) {
            this.innerCircle.fill(podInnerAboardColor);
            this.outerCircle.fill(podOuterAboardColor);
        } else {
            this.innerCircle.fill(podInnerEmptyColor);
            this.outerCircle.fill(podOuterEmptyColor);
        }
    }

    updateScale(value) {
        this.innerCircle.scaleX(value);
        this.innerCircle.scaleY(value);
        this.outerCircle.scaleX(value);
        this.outerCircle.scaleY(value);
    }

    isAboard() {
        return this.travelerNumber > 0;
    }
}

export function updatePodFromJSON(podJSON) {
    let targetPods = appState.objects.filter(pod => pod.uuid.includes(podJSON["name"]));

    if (targetPods.length <= 0) {
        new Pod(podJSON).updateScale(appState.objectScale);
    } else {
        targetPods.forEach(pod => pod.update(podJSON));
    }
}