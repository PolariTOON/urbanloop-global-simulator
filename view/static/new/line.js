import {state} from "./state.js";
import {Legend} from "./legend.js";
import {Pod} from "./pod.js";
const {Group} = Konva;

export class Line extends Group {
    // __legend;
    // __name;
    // __x;
    // __y;
    constructor(legendsLayer) {
        const text = new Legend();
        super();
        legendsLayer.add(text);
        this.__legend = text;
    }
    set _name(value) {
        this.__name = value;
        this.__legend._name = value;
    }
    get _name() {
        return this.__name;
    }
    set _x(value) {
        super.x(value);
        super.offsetX(value);
        this.__x = value;
        this.__legend._x = value;
    }
    get _x() {
        return this.__x;
    }
    set _y(value) {
        super.y(value);
        super.offsetY(value);
        this.__y = value;
        this.__legend._y = value;
    }
    get _y() {
        return this.__y;
    }
    update(json, loopsJSON, podsLayer, hintsLayer) {
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
            pod.update(p, json, loopsJSON);
        }
    }
    scale(...args) {
        const that = super.scale(...args);
        if (that !== this) {
            return that;
        }
        const {x, y} = super.scale();
        this.__legend.scale({
            x,
            y,
        });
        return that;
    }
    destroy() {
        const that = super.destroy();
        this.__legend.destroy();
        return that;
    }
}
