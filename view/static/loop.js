import {state} from "./state.js";
import {Line} from "./line.js";
import {Section} from "./section.js";

function averagePoint(elements) {
    let x = 0;
    let y = 0;
    for (const element of elements) {
        x += element["x"];
        y += element["y"];
    }
    x /= elements.length;
    y /= elements.length;
    return {x, y};
}

export class Loop extends Line {
    // __elements;
    // __sections;
    constructor(json, legendsLayer, elementsLayer, sectionsLayer, hintsLayer) {
        const elementsJSON = json["elements"];
        const sectionsJSON = json["sections"];
        super(elementsJSON, legendsLayer, elementsLayer, sectionsLayer, hintsLayer);
        // building sections
        for (let i = 0, li = sectionsJSON.length; i < li; i++) {
            const pathType = sectionsJSON[i]["path"]["type"];
            const beginElement = this.__elements[i];
            const endElement = this.__elements[(i + 1) % li];
            const loopOrBridge = true;
            const section = new Section(pathType, beginElement, endElement, loopOrBridge, hintsLayer);
            this.__sections.push(section);
            sectionsLayer.add(section);
            state.nodes.push(section);
        }
    }
    update(json, podsLayer, hintsLayer, showWaitingTravelers) {
        const name = json["name"];
        const {x, y} = averagePoint(json["elements"]);
        this._name = name;
        this._x = x;
        this._y = y;
        const elementsJSON = json["elements"];
        const sectionsJSON = json["sections"];
        super.update(json, null, elementsJSON, sectionsJSON, podsLayer, hintsLayer, showWaitingTravelers);
    }
}
