import {state} from "./state.js";
import {Line} from "./line.js";
import {Section} from "./section.js";

export class Bridge extends Line {
    // __switchOut;
    // __switchIn;
    // __section;
    constructor(json, switchOut, switchIn, legendsLayer, sectionsLayer, hintsLayer) {
        const section = new Section(json["section"]["path"]["type"], switchOut, switchIn, false, hintsLayer);
        sectionsLayer.add(section);
        state.nodes.push(section);
        super(legendsLayer);
        this.__switchOut = switchOut;
        this.__switchIn = switchIn;
        this.__section = section;
    }
    set _switchOut(value) {
        this.__switchOut = value;
    }
    get _switchOut() {
        return this.__switchOut;
    }
    set _switchIn(value) {
        this.__switchOut = value;
    }
    get _switchIn() {
        return this.__switchIn;
    }
    set _section(value) {
        this.__section = value;
    }
    get _section() {
        return this.__section;
    }
    update(json, loopsJSON, podsLayer, hintsLayer) {
        const name = json["name"];
        const x = (this.__switchOut.x() + this.__switchIn.x()) / 2;
        const y = (this.__switchOut.y() + this.__switchIn.y()) / 2;
        this._name = name;
        this._x = x;
        this._y = y;
        this.__section.update(json["section"]);
        super.update(json, loopsJSON, podsLayer, hintsLayer);
    }
}
