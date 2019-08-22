import {Entity} from "./entity.js";
const {Circle} = Konva;

const shadowColor = "#333"
const outerColor = "#fc0";
const innerColor = "#fff";
const selectedOuterColor = "#0fc";
const fullInnerColor = "#333";

function distanceBetween(beginElement, endElement, path) {
    let d = 0;
    switch (path["type"]) {
        case "line":
        default: {
            d = Math.hypot(beginElement["x"] - endElement["x"], beginElement["y"] - endElement["y"]);
            break;
        }
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
            } else {
                break;
            }
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
            break;
        }
    }
    return {x, y};
}

export class Pod extends Entity {
    // __outerShape;
    // __innerShape;
    // __travelerCount;
    // __travelerMax;
    // __keepFlag;
    constructor(json, lineJSON, loopsJSON, infoLayer) {
        const outerShape = new Circle({
            lineJoin: "round",
            lineCap: "round",
            radius: 10,
            strokeWidth: 1,
            stroke: shadowColor,
        });
        const innerShape = new Circle({
            listening: false,
            lineJoin: "round",
            lineCap: "round",
            radius: 5,
            strokeWidth: 1,
            stroke: shadowColor,
        });
        const keepFlag = 0;
        super(infoLayer);
        super.add(outerShape);
        super.add(innerShape);
        this.__outerShape = outerShape;
        this.__innerShape = innerShape;
        this.update(json, lineJSON, loopsJSON);
        this._keepFlag = keepFlag;
        this.unselect();
    }
    set _x(value) {
        super._x = value;
        this.__outerShape.x(value);
        this.__innerShape.x(value);
    }
    get _x() {
        return super._x;
    }
    set _y(value) {
        super._y = value;
        this.__outerShape.y(value);
        this.__innerShape.y(value);
    }
    get _y() {
        return super._y;
    }
    set _travelerCount(value) {
        this.__travelerCount = value;
        if (value === 0) {
            this.__innerShape.fill(innerColor);
        } else {
            this.__innerShape.fill(fullInnerColor);
        }
    }
    get _travelerCount() {
        return this.__travelerCount;
    }
    set _travelerMax(value) {
        this.__travelerMax = value;
    }
    get _travelerMax() {
        return this.__travelerMax;
    }
    set _keepFlag(value) {
        this.__keepFlag = value;
    }
    get _keepFlag() {
        return this.__keepFlag;
    }
    select() {
        this.__outerShape.fill(selectedOuterColor);
    }
    unselect() {
        this.__outerShape.fill(outerColor);
    }
    update(json, lineJSON, loopsJSON) {
        const name = json["name"];
        const {x, y} = xyFromPosition(json, lineJSON, loopsJSON);
        const travelerCount = json["travelers"]["count"];
        const travelerMax = json["travelers"]["max"];
        this._name = name;
        this._x = x;
        this._y = y;
        this._travelerCount = travelerCount;
        this._travelerMax = travelerMax;
    }
}
