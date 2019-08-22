import {Entity} from "./entity.js";
const {Circle} = Konva;

const shadowColor = "#333"
const outerColor = "#fc0";
const innerColor = "#fff";
const selectedOuterColor = "#0fc";
const fullInnerColor = "#333";

function calcLength(startElement, endElement, path) {
    let d = 0;
    switch (path["type"]) {
        case "line":
        default: {
            d += Math.hypot(startElement["x"] - endElement["x"], startElement["y"] - endElement["y"]);
            break;
        }
    }
    return d;
}

function calcPosition(json, lineJSON, loopsJSON){
    let startElement;
    let endElement;
    let path;
    let length;
    let position = json["position"];
    if (loopsJSON) {
        const loopStartElement = lineJSON["switch_out"]["loop"];
        const loopEndElement = lineJSON["switch_in"]["loop"];
        const startElementIndex = lineJSON["switch_out"]["element"];
        const endElementIndex = lineJSON["switch_in"]["element"];
        startElement = loopsJSON[loopStartElement]["elements"][startElementIndex];
        endElement = loopsJSON[loopEndElement]["elements"][endElementIndex];
        path = lineJSON["section"]["path"];
        length = calcLength(startElement, endElement, path);
    } else {
        let index = 0;
        while (true) {
            startElement = lineJSON["elements"][index];
            endElement = lineJSON["elements"][(index + 1) % lineJSON["elements"].length];
            path = lineJSON["sections"][index]["path"];
            length = calcLength(startElement, endElement, path);
            if (position < length) {
                break;
            }
            position -= length;
            index++;
        }
    }
    let x = startElement["x"];
    let y = startElement["y"];
    switch (path["type"]) {
        case "line":
        default: {
            const ratio = position / length;
            x += (endElement["x"] - startElement["x"]) * ratio;
            y += (endElement["y"] - startElement["y"]) * ratio;
            break;
        }
    }
    return {x, y, position};
}

export class Pod extends Entity {
    // __outerShape;
    // __innerShape;
    // __position;
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
    set _position(value) {
        this.__position = value;
    }
    get _position() {
        return this.__position;
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
        const {x, y, position} = calcPosition(json, lineJSON, loopsJSON);
        const travelerCount = json["travelers"]["count"];
        const travelerMax = json["travelers"]["max"];
        this._name = name;
        this._x = x;
        this._y = y;
        this._position = position;
        this._travelerCount = travelerCount;
        this._travelerMax = travelerMax;
    }
}
