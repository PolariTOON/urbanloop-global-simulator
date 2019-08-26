import {Entity} from "./entity.js";
const {Star} = Konva;

const shadowColor = "#333"
const outerColor = "#f03";
const innerColor = "#fff";
const selectedOuterColor = "#0fc";

export class Sensor extends Entity {
    // __outerShape;
    // __innerShape;
    constructor(hintsLayer) {
        const outerShape = new Star({
            lineJoin: "round",
            lineCap: "round",
            numPoints: 5,
            outerRadius: 20,
            innerRadius: 10,
            strokeWidth: 1,
            stroke: shadowColor,
        });
        const innerShape = new Star({
            listening: false,
            lineJoin: "round",
            lineCap: "round",
            numPoints: 5,
            outerRadius: 10,
            innerRadius: 5,
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
        this._name = name;
        this._x = x;
        this._y = y;
    }
}
