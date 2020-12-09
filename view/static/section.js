import {Entity} from "./entity.js";
const {Arrow} = Konva;

const shadowColor = "#333"
const pathColor = "#333";
const selectedPathColor = "#0fc";

const closeButton = document.getElementById("close-button").control;

const outerStrokeWidth = 2;
const innerStrokeWidth = 1;
const pointerLength = 8;
const pointerWidth = 6;
const loopDashSize = 10;
const loopDashMargin = 10;
const bridgeDashSize = 0;
const bridgeDashMargin = 10;

export class Section extends Entity {
    // __outerPath;
    // __innerPath;
    // __pathType;
    // __startElement;
    // __endElement;
    // __loopOrBridge;
    // __speed;
    // __length;
    constructor(pathType, startElement, endElement, loopOrBridge, hintsLayer) {
        let outerPath;
        let innerPath;
        switch (pathType) {
            case "line":
            default: {
                outerPath = new Arrow({
                    lineJoin: "round",
                    lineCap: "round",
                    strokeWidth: outerStrokeWidth,
                    pointerLength: pointerLength,
                    pointerWidth: pointerWidth,
                    dash: [
                        loopOrBridge ? loopDashSize : bridgeDashSize,
                        loopOrBridge ? loopDashMargin : bridgeDashMargin,
                    ],
                    dashEnabled: true,
                    fill: shadowColor,
                    stroke: shadowColor,
                });
                innerPath = new Arrow({
                    listening: false,
                    lineJoin: "round",
                    lineCap: "round",
                    strokeWidth: innerStrokeWidth,
                    pointerLength: pointerLength,
                    pointerWidth: pointerWidth,
                    dash: [
                        loopOrBridge ? loopDashSize : bridgeDashSize,
                        loopOrBridge ? loopDashMargin : bridgeDashMargin,
                    ],
                    dashEnabled: true,
                });
                break;
            }
        }
        super(hintsLayer);
        super.add(outerPath);
        super.add(innerPath);
        this.__outerPath = outerPath;
        this.__innerPath = innerPath;
        this.__pathType = pathType;
        this.__startElement = startElement;
        this.__endElement = endElement;
        this.__loopOrBridge = loopOrBridge;
        this.__closed = 0;
        this.unselect();
    }
    set _startElement(value) {
        this.__startElement = value;
    }
    get _startElement() {
        return this.__startElement;
    }
    set _endElement(value) {
        this.__endElement = value;
    }
    get _endElement() {
        return this.__endElement;
    }
    set _x(value) {
        super._x = value;
        this.__outerPath.x(value);
        this.__outerPath.offsetX(value);
        this.__innerPath.x(value);
        this.__innerPath.offsetX(value);
    }
    get _x() {
        return super._x;
    }
    set _y(value) {
        super._y = value;
        this.__outerPath.y(value);
        this.__outerPath.offsetY(value);
        this.__innerPath.y(value);
        this.__innerPath.offsetY(value);
    }
    get _y() {
        return super._y;
    }
    set _speed(value) {
        this.__speed = value;
    }
    get _speed() {
        return this.__speed;
    }
    set _length(value) {
        this.__length = value;
    }
    get _length() {
        return this.__length;
    }
    set _closed(value) {
        this.__closed = value;
    }
    get _closed() {
        return this.__closed;
    }
    select() {
        closeButton.style.display = "block"
        if (this.__closed == 0){
            closeButton["value"] = "Close section"
            this.__innerPath.fill(selectedPathColor);
            this.__innerPath.stroke(selectedPathColor);
        }
        else{
            closeButton["value"] = "Open section"
        }
    }
    unselect() {
        closeButton.style.display = "none"
        if (this.__closed == 0){
            this.__innerPath.fill(pathColor);
            this.__innerPath.stroke(pathColor);
        }
    }   
    scale(...args) {
        const that = super.scale(...args);
        if (that !== this) {
            return that;
        }
        const {x, y} = super.scale();
        const scale = Math.exp(Math.log(x * y) / 2);
        this.__outerPath.scale({
            x: 1 / x,
            y: 1 / y,
        });
        this.__outerPath.strokeWidth(outerStrokeWidth * scale);
        this.__outerPath.pointerLength(pointerLength * scale);
        this.__outerPath.pointerWidth(pointerWidth * scale);
        this.__outerPath.dash([
            (this.__loopOrBridge ? loopDashSize : bridgeDashSize) * scale,
            (this.__loopOrBridge ? loopDashMargin : bridgeDashMargin) * scale,
        ]);
        this.__innerPath.scale({
            x: 1 / x,
            y: 1 / y,
        });
        this.__innerPath.strokeWidth(innerStrokeWidth * scale);
        this.__innerPath.pointerLength(pointerLength * scale);
        this.__innerPath.pointerWidth(pointerWidth * scale);
        this.__innerPath.dash([
            (this.__loopOrBridge ? loopDashSize : bridgeDashSize) * scale,
            (this.__loopOrBridge ? loopDashMargin : bridgeDashMargin) * scale,
        ]);
        return that;
    }
    update(json) {
        const name = json["name"];
        const x = (this.__startElement._x + this.__endElement._x) / 2;
        const y = (this.__startElement._y + this.__endElement._y) / 2;
        const speed = json["speed"];
        const length = json["length"];
        this.__outerPath.points([
            this.__startElement._x,
            this.__startElement._y,
            this.__endElement._x,
            this.__endElement._y,
        ]);
        this.__innerPath.points([
            this.__startElement._x,
            this.__startElement._y,
            this.__endElement._x,
            this.__endElement._y,
        ]);
        this._name = name;
        this._x = x;
        this._y = y;
        this._speed = speed;
        this._length = length;
    }
}
