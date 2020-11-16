import {state} from "./state.js";
import {Line} from "./line.js";
import {Section} from "./section.js";
import {Sensor} from "./sensor.js";
import {Shed} from "./shed.js";
import {Station} from "./station.js";
import {Switch} from "./switch.js";

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
        const elements = [];
        const sections = [];
        const elementsJSON = json["elements"];
        const sectionsJSON = json["sections"];
        for (let i = 0, li = elementsJSON.length; i < li; i++) {
            let element;
            switch (elementsJSON[i]["type"]) {
                case "station": {
                    element = new Station(hintsLayer);
                    break;
                }
                case "shed": {
                    element = new Shed(hintsLayer);
                    break;
                }
                case "sensor": {
                    element = new Sensor(hintsLayer);
                    break;
                }
                case "switch_in":
                case "switch_out": {
                    element = new Switch(hintsLayer);
                    break;
                }
            }
            elements.push(element);
            elementsLayer.add(element);
            state.nodes.push(element);
        }
        for (let i = 0, li = sectionsJSON.length; i < li; i++) {
            const pathType = sectionsJSON[i]["path"]["type"];
            const beginElement = elements[i];
            const endElement = elements[(i + 1) % li];
            const loopOrBridge = true;
            const section = new Section(pathType, beginElement, endElement, loopOrBridge, hintsLayer);
            sections.push(section);
            sectionsLayer.add(section);
            state.nodes.push(section);
        }
        super(legendsLayer);
        this.__elements = elements;
        this.__sections = sections;
    }
    set _elements(value) {
        this.__elements = value;
    }
    get _elements() {
        return this.__elements;
    }
    set _sections(value) {
        this.__sections = value;
    }
    get _sections() {
        return this.__sections;
    }
    update(json, podsLayer, hintsLayer, showing_travelers_waiting) {
        const name = json["name"];
        const {x, y} = averagePoint(json["elements"]);
        this._name = name;
        this._x = x;
        this._y = y;
        const elementsJSON = json["elements"];
        const sectionsJSON = json["sections"];
        for (let i = 0, li = elementsJSON.length; i < li; i++) {
            if (this.__elements[i] instanceof Switch) {
                this.__elements[i].update(elementsJSON[i], podsLayer, hintsLayer);
            } 
            else 
            {
                if (this.__elements[i] instanceof Station)
                {
                    this.__elements[i].update(elementsJSON[i], showing_travelers_waiting);
                }
                else
                {
                    this.__elements[i].update(elementsJSON[i]);
                }
            }
        }
        for (let i = 0, li = sectionsJSON.length; i < li; i++) {
            this.__sections[i].update(sectionsJSON[i]);
        }
        super.update(json, null, podsLayer, hintsLayer);
    }
}
