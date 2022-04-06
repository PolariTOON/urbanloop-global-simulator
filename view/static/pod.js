import {Entity} from "./entity.js";
const {Circle} = Konva;

const shadowColor = "#333"
const outerColor = "#fc0";
const outerColorWhenCommanded = "#1f6";                                 // vert
const outerColorWhenCommandedAndChangedDest = "#f1A";                   // pink
const outerColorWhenCommandedAndEmergencyExit = "#f70";                 // orange
const outerColorWhenCommandedAndChangedDestAndEmergencyExit = "#b61";   // marron
const failingOuterColor = "#ff0707";
const innerColor = "#fff";
const selectedOuterColor = "#0fc";
const fullInnerColor = "#333";

const outerColor_VersRevision = "#d2b"; //p_tb
const outerColor_VersLavage = "#888"; //p_tb

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
    let elements;
    let sections = lineJSON["sections"];
    if (loopsJSON !== null) {  // Pod in a Bridge
        // find the switches in loopJSON
        const switchOutLoop = lineJSON["switch_out"]["loop"];
        const switchInLoop = lineJSON["switch_in"]["loop"];
        const switchOutIndex = lineJSON["switch_out"]["element"];
        const switchInIndex = lineJSON["switch_in"]["element"];
        const switchOut = loopsJSON[switchOutLoop]["elements"][switchOutIndex];
        const switchIn = loopsJSON[switchInLoop]["elements"][switchInIndex];
        // create an array containing both the switches and the elements :
        // [switch_out, element 1, element 2, ..., switch in]
        elements = [switchOut].concat(lineJSON["elements"]).concat(switchIn);
    } else {  // Pod in a Loop
        elements = lineJSON["elements"];
    }
    let index = 0;
    while (true) {
        startElement = elements[index];
        endElement = elements[(index + 1) % elements.length];
        path = sections[index]["path"];
        length = calcLength(startElement, endElement, path);
        if (position < length) {
            break;
        }
        position -= length;
        index++;
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

function calcPosition(json, lineJSON, loopsJSON) {
    if (lineJSON !== null) {
        return calcPositionInSection(json, lineJSON, loopsJSON);
    } else {
        return calcPositionInSwitch(json, loopsJSON);
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
/*
        outerShape.perfectDrawEnabled(false);
        innerShape.perfectDrawEnabled(false);
        outerShape.listening(false);
        innerShape.listening(false);
*/
        super.add(outerShape);
        super.add(innerShape);
        this.__outerShape = outerShape;
        this.__innerShape = innerShape;
        this._outerColor = outerColor;
        this._outerColorWhenCommanded = outerColorWhenCommanded;
        this.outerColorWhenCommandedAndChangedDest = outerColorWhenCommandedAndChangedDest;
        this.outerColorWhenCommandedAndEmergencyExit = outerColorWhenCommandedAndEmergencyExit;
        this.outerColorWhenCommandedAndChangedDestAndEmergencyExit = outerColorWhenCommandedAndChangedDestAndEmergencyExit;
        this._failing = false;
        this._contain_real_user = false;
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
    set _travelerCount(value) 
    {
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
        } 
        else 
        {
            if (this._contain_real_user)
            {
                this.__outerShape.fill(outerColorWhenCommandedByUser); 
            }
            else
            {
                this.__outerShape.fill(outerColor); 
            }
        }
    }
    update(json, lineJSON, loopsJSON) {
        const name = json["name"];
        const speed = json["speed"];
        const {x, y, position} = calcPosition(json, lineJSON, loopsJSON);
        const travelerCount = json["travelers"]["count"];
        const travelerMax = json["travelers"]["max"];
        const source = json["source"];
        const destination = json["destination"];
        const failing = json["failing"];
        this._contain_real_user = json["contain_real_user"];
        this._changed_destination = json["changed_destination"];
        this._emergency_exit = json["emergency_exit"];
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

        this.__en_direction_revision = json["en_direction_revision"]//p_tb
        this.__en_direction_lavage = json["en_direction_lavage"]//p_tb

        if (this._contain_real_user)
        {   
            if (this._changed_destination)
            {
                if (this._emergency_exit)
                {
                    this.__outerShape.fill(outerColorWhenCommandedAndChangedDestAndEmergencyExit); 
                }
                else
                {
                    this.__outerShape.fill(outerColorWhenCommandedAndChangedDest); 
                }
            }
            else
            {
                if (this._emergency_exit)
                {
                    this.__outerShape.fill(outerColorWhenCommandedAndEmergencyExit); 
                }
                else
                {
                    this.__outerShape.fill(outerColorWhenCommanded); 
                }
            }
        }
        else
        {
            //p_tb this.__outerShape.fill(outerColor);
            if(this.__en_direction_revision){
            	this.__outerShape.fill(outerColor_VersRevision);
            }
            else if(this.__en_direction_lavage) {
            	this.__outerShape.fill(outerColor_VersLavage);
            }
            else
            {
            	this.__outerShape.fill(outerColor);
            }
        }
    }
}
