import {Entity} from "./entity.js";
const {RegularPolygon} = Konva;

const shadowColor = "#333"
const outerColor = "#f03";
const innerColor = "#fff";
const selectedOuterColor = "#0fc";

export class Shed extends Entity {
    // __outerShape;
    // __innerShape;
    // __podCount;
    // __podMax;
    constructor(hintsLayer) {
        const outerShape = new RegularPolygon({
            lineJoin: "round",
            lineCap: "round",
            sides: 4,
            radius: 20,
            strokeWidth: 1,
            stroke: shadowColor,
        });
        const innerShape = new RegularPolygon({
            listening: false,
            lineJoin: "round",
            lineCap: "round",
            sides: 4,
            radius: 13,
            strokeWidth: 1,
            fill: innerColor,
            stroke: shadowColor,
        });
        super(hintsLayer);
        super.add(outerShape);
        super.add(innerShape);
        this.__outerShape = outerShape;
        this.__innerShape = innerShape;
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
    set _podCount(value) {
        this.__podCount = value;
    }
    get _podCount() {
        return this.__podCount;
    }
    set _podMax(value) {
        this.__podMax = value;
    }
    get _podMax() {
        return this.__podMax;
    }
    select() {
        this.__outerShape.fill(selectedOuterColor);
    }
    unselect() {
        this.__outerShape.fill(outerColor);
    }
    update(json) {
        const name = json["name"];
        const x = json["x"];
        const y = json["y"];
        const podCount = json["pods"]["count"];
        const podMax = json["pods"]["max"];
        this._name = name;
        this._x = x;
        this._y = y;
        this._podCount = podCount;
        this._podMax = podMax;
       // this.__outerShape.cache();
       // this.__innerShape.cache();
    }
}
