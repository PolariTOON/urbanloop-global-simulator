import {appState} from "./network.js";
const {Circle, Group, Label, Tag, Text} = Konva;

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
            d = Math.hypot(beginElement["x"] - endElement["x"], beginElement["y"] - endElement["y"]);
    }
    return d;
}

function xyFromPosition(json, lineJSON, loopsJSON){
    let d = 0;
    let path;
    let xy;
    let beginElement, endElement;
    if (loopsJSON){
        d = json["position"];
        const loopBeginElement = lineJSON["switch_out"]["loop"];
        const loopEndElement = lineJSON["switch_in"]["loop"];
        const beginElementIndex = lineJSON["switch_out"]["element"];
        const endElementIndex = lineJSON["switch_in"]["element"];
        beginElement = loopsJSON[loopBeginElement]["elements"][beginElementIndex];
        endElement = loopsJSON[loopEndElement]["elements"][endElementIndex];
        path = lineJSON["section"]["path"];
        xy = [beginElement["x"], beginElement["y"]];
    } else {
        const loopSize = lineJSON["elements"].length;
        let index = 0;
        let distanceToNext = 0;
        while (d < json["position"]){
            beginElement = lineJSON["elements"][index];
            endElement = lineJSON["elements"][(index+1)%loopSize];
            path = lineJSON["sections"][index]["path"];
            distanceToNext = distanceBetween(beginElement, endElement, path);
            if (d + distanceToNext < json["position"]){
                d += distanceToNext;
                ++index;
            }
            else
                break;
        }
        d = json["position"] - d;
        beginElement = lineJSON["elements"][index];
        endElement = lineJSON["elements"][(index+1)%loopSize];
        path = lineJSON["sections"][index]["path"];
        xy = [lineJSON["elements"][index]["x"], lineJSON["elements"][index]["y"]];
    }
    const D = distanceBetween(beginElement, endElement, path);
    switch (path["type"]){
            case "line":
            default:
                const coeff = d / D;
                xy[0] += coeff * (endElement["x"] - beginElement["x"]);
                xy[1] += coeff * (endElement["y"] - beginElement["y"]);
        }
    return xy;

}

export class Pod extends Group {
    constructor(json, lineJSON, isDocked, loopsJSON, infoLayer) {
        const name = json["name"];
        const xy = xyFromPosition(json, lineJSON, loopsJSON);
        const x = xy[0];
        const y = xy[1];
        const podWidth = 5;
        super({
            name,
            x,
            y,
            offsetX: x,
            offsetY: y
        });
        this.travelerNumber = json["travelers"]["count"];
        this.isDocked = isDocked;

        this.innerCircle = new Circle({
            x,
            y,
            radius: podWidth - Math.sqrt(podWidth),
        });

        this.outerCircle = new Circle({
            x,
            y,
            radius: podWidth,
        });

        this.info = new Label({
            x,
            y,
            opacity: 0.75,
            visible: false,
            listening: false
        });

        this.info.add(
            new Tag({
                fill: "black",
                pointerDirection: "down",
                pointerWidth: 10,
                pointerHeight: 10,
                lineJoin: "round",
                shadowColor: "black",
                shadowBlur: 10,
                shadowOffset: 10,
                shadowOpacity: 0.2
            })
        );

        this.info.add(
            new Text({
                text: "Pod : " + json["name"] + " | Capacity : " + json["travelers"]["max"],
                fontFamily: "Calibri",
                fontSize: 18,
                padding: 5,
                fill: "white"
            })
        );

        this.add(this.outerCircle);
        this.add(this.innerCircle);
        infoLayer.add(this.info);
        this.update();
        appState.objects.push(this);
    }

    select() {
        this.innerCircle.fill(podInnerSelectedColor);
        this.outerCircle.fill(podOuterSelectedColor);
    }

    unselect() {
        this.updateColor();
    }

    update(json) {
        /*this.isDocked = !json['moving'];
        this.travelerNumber = json["travelers"]["count"];*/
        this.json = json;
        //this.track = json['currentElementUuid']; TODO: à gérer

        /*if (this.isDocked) {
            if (json['stationIndex'] === -1) { // THIS IS HOTFIX FOR GHOST CAPS
                this.innerCircle.hide();
                this.outerCircle.hide();
                return;
            }
            let targetStations = appState.objects.filter(station => station.uuid.includes(json['currentElementUuid']));
            targetStations.forEach(station => {
                this.innerCircle.x(x + 10 * station.stationRadius + (6 * json['stationIndex'] + 2) * station.dockSize);
                this.outerCircle.x(x + 10 * station.stationRadius + (6 * json['stationIndex'] + 2) * station.dockSize);
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

export function updatePodFromJSON(json) {
    let targetPods = appState.objects.filter(pod => pod.uuid.includes(json["name"]));

    if (targetPods.length <= 0) {
        new Pod(json).updateScale(appState.objectScale); // TODO: ajouter les capsules quelque part
    } else {
        targetPods.forEach(pod => pod.update(json));
    }
}
