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

export class Pod extends Entity {
    constructor(json, lineJSON, isDocked, loopsJSON, infoLayer) {
        const name = json["name"];
        const xy = xyFromPosition(json, lineJSON, loopsJSON);
        const x = xy[0];
        const y = xy[1];
        const podWidth = 5;
        const label = "Pod : " + json["name"] + " | Capacity : " + json["travelers"]["max"];
        super({
            name,
            label,
            x,
            y,
            offsetX: x,
            offsetY: y
        }, infoLayer);
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
}
