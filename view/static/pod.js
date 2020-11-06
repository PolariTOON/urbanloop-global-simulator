import {Entity} from "./entity.js";
const {Circle} = Konva;

const shadowColor = "#333"
const outerColor = "#fc0";
const failingOuterColor = "#ff0707";
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

function calcPositionInSwitch(json, switchJSON) {
    const x = switchJSON["x"];
    const y = switchJSON["y"];
    const position = json["position"];
    return {x, y, position};
}

function calcPositionInSection(json, lineJSON, loopsJSON) {
    let startElement;
    let endElement;
    let path;
    let length;
    let position = json["position"];
    if (loopsJSON !== null) {
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

function calcPosition(json, json2, json3) {
    if (json2 !== null) {
        return calcPositionInSection(json, json2, json3);
    } else {
        return calcPositionInSwitch(json, json3);
    }
}

export class Pod extends Entity {
    // __outerShape;
    // __innerShape;
    // __position;
    // __travelerCount;
    // __travelerMax;
    // __speed;
    // __source; // TODO
    // __destination; // TODO
    // __keepFlag;
    constructor(hintsLayer) {
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
        super(hintsLayer);
        super.add(outerShape);
        super.add(innerShape);
        this.__outerShape = outerShape;
        this.__innerShape = innerShape;
        this._outerColor = outerColor;
        this._failing = false;
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
    get _speed(){
        return this.__speed;
    }
    set _speed(value){
        this.__speed = value;
    }
    set _keepFlag(value) {
        this.__keepFlag = value;
    }
    get _keepFlag() {
        return this.__keepFlag;
    }
    get _source(){
        return this.__source;
    }
    set _source(value){
        this.__source = value
    }
    get _destination(){
        return this.__destination;
    }
    set _destination(value){
        this.__destination = value;
    }
    select() {
        this.__outerShape.fill(selectedOuterColor);
    }
    unselect() {
        if (this._failing) {
            this.__outerShape.fill(failingOuterColor);
        } else {
            this.__outerShape.fill(outerColor); 
        }
    }
    update(json, json2, json3) {
        const name = json["name"];
        const speed = json["speed"];
        const {x, y, position} = calcPosition(json, json2, json3);
        const travelerCount = json["travelers"]["count"];
        const travelerMax = json["travelers"]["max"];
        const source = json["source"];
        const destination = json["destination"];
        const failing = json["failing"];
        this._name = name;
        this._x = x;
        this._y = y;
        this._position = position;
        this._travelerCount = travelerCount;
        this._travelerMax = travelerMax;
        this._speed = speed;
        this._source = source;
        this._destination = destination;
        if (failing && !this.failing) {
            this.__outerShape.fill(failingOuterColor);
        }
        this._failing = failing;
    }
}
