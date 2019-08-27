import {state} from "./state.js";
import {Entity} from "./entity.js";
import {Pod} from "./pod.js";
const {Circle} = Konva;

const shadowColor = "#333";
const outerColor = "#03f";
const innerColor = "#fff";
const selectedOuterColor = "#0fc";

export class Switch extends Entity {
    // __outerShape;
    // __innerShape;
    // __speed;
    // __length;
    constructor(hintsLayer) {
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
    select() {
        this.__outerShape.fill(selectedOuterColor);
    }
    unselect() {
        this.__outerShape.fill(outerColor);
    }
    update(json, podsLayer, hintsLayer) {
        const name = json["name"];
        const x = json["x"];
        const y = json["y"];
        const speed = json["speed"];
        const length = json["length"];
        this._name = name;
        this._x = x;
        this._y = y;
        this._speed = speed;
        this._length = length;
        for (const p of json["pods"]) {
            let pod;
            if (state.pods.has(p["id"])) {
                pod = state.pods.get(p["id"]);
                pod._keepFlag = 1;
            } else {
                pod = new Pod(hintsLayer);
                podsLayer.add(pod);
                state.pods.set(p["id"], pod);
                pod._keepFlag = 2;
            }
            pod.update(p, null, json);
        }
    }
}
