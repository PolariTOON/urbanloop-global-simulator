import {Entity} from "./entity.js";
const {Circle} = Konva;

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
    let x;
    let y;
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
        x = beginElement["x"];
        y = beginElement["y"];
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
        x = lineJSON["elements"][index]["x"];
        y = lineJSON["elements"][index]["y"];
    }
    const D = distanceBetween(beginElement, endElement, path);
    switch (path["type"]) {
        case "line":
        default: {
            const coeff = d / D;
            x += coeff * (endElement["x"] - beginElement["x"]);
            y += coeff * (endElement["y"] - beginElement["y"]);
        }
    }
    return {x, y};
}

export class Pod extends Entity {
    constructor(json, lineJSON, loopsJSON, infoLayer) {
        const name = json["name"];
        const {x, y} = xyFromPosition(json, lineJSON, loopsJSON);
        const podWidth = 5;
        const label = "Pod : " + json["name"] + " | Capacity : " + json["travelers"]["max"];
        super({
            name,
            label,
            x,
            y,
            offsetX: x,
            offsetY: y,
        }, infoLayer);
        this.updateCount = 0;
        this.travelerNumber = json["travelers"]["count"];
        this.keepFlag = 0;
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
        this.add(this.outerCircle);
        this.add(this.innerCircle);
        this.unselect();
    }
    select() {
        this.innerCircle.fill(podInnerSelectedColor);
        this.outerCircle.fill(podOuterSelectedColor);
    }
    unselect() {
        if (this.travelerNumber > 0) {
            this.innerCircle.fill(podInnerAboardColor);
            this.outerCircle.fill(podOuterAboardColor);
        } else {
            this.innerCircle.fill(podInnerEmptyColor);
            this.outerCircle.fill(podOuterEmptyColor);
        }
    }
    update(json, lineJSON, loopsJSON) {
        const xy = xyFromPosition(json, lineJSON, loopsJSON);
        super.update(xy);
        this.position(xy);
        this.offset(xy);
        this.innerCircle.position(xy);
        this.outerCircle.position(xy);
        this.outerCircle.position(xy);
    }
}
