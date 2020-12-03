import {state} from "./state.js";
import {Line} from "./line.js";
import {Section} from "./section.js";

export class Bridge extends Line {
    // __switchOut;
    // __switchIn;
    // __elements;
    // __sections;
    constructor(json, switchOut, switchIn, elementsLayer, legendsLayer, sectionsLayer, hintsLayer) {
        const elementsJSON = json["elements"];
        const sectionsJSON = json["sections"];
        super(elementsJSON, legendsLayer, elementsLayer, sectionsLayer, hintsLayer);
        // building sections
        for (let i = 0, li = sectionsJSON.length; i < li; i++) {
            const pathType = sectionsJSON[i]["path"]["type"];
            const loopOrBridge = false; // we are on a bridge, not a loop
            const section = new Section(pathType, null, null, loopOrBridge, hintsLayer);
            this.__sections.push(section);
            sectionsLayer.add(section);
            state.nodes.push(section);
        }
        for (let i = 0, li = sectionsJSON.length; i < li; i++) {
            this.__sections[i]._startElement = (i == 0) ? switchOut : this.__elements[i-1];
            this.__sections[i]._endElement = (i == li - 1) ? switchIn : this.__elements[i];
        }
        this.__switchOut = switchOut;
        this.__switchIn = switchIn;
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
    update(json, loopsJSON, podsLayer, hintsLayer, showWaitingTravelers) {
        const name = json["name"];
        const elementsJSON = json["elements"];
        const sectionsJSON = json["sections"];
        const x = (this.__switchOut.x() + this.__switchIn.x()) / 2;
        const y = (this.__switchOut.y() + this.__switchIn.y()) / 2;
        this._name = name;
        this._x = x;
        this._y = y;
        super.update(json, loopsJSON, elementsJSON, sectionsJSON, podsLayer, hintsLayer, showWaitingTravelers);
    }
}
