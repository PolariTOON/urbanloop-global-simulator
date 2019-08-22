import {Entity} from "./entity.js";
const {Circle} = Konva;

const shadowColor = "#333"
const outerColor = "#03f";
const innerColor = "#fff";
const selectedOuterColor = "#0fc";

export class Switch extends Entity {
    // __outerShape;
    // __innerShape;
    constructor(json, infoLayer) {
        const outerShape = new Circle({
            lineJoin: "round",
            lineCap: "round",
            radius: 16,
            strokeWidth: 1,
            stroke: shadowColor,
        });
        const innerShape = new Circle({
            listening: false,
            lineJoin: "round",
            lineCap: "round",
            radius: 11,
            strokeWidth: 1,
            fill: innerColor,
            stroke: shadowColor,
        });
        super(infoLayer);
        super.add(outerShape);
        super.add(innerShape);
        this.__outerShape = outerShape;
        this.__innerShape = innerShape;
        this.update(json);
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
