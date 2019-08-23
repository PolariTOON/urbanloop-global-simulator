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
    constructor(json, networkLayer, infoLayer) {
        const elements = [];
        const sections = [];
        for (let i = 0, li = json["elements"].length; i < li; i++) {
            let element;
            switch (json["elements"][i]["type"]) {
                case "station": {
                    element = new Station(infoLayer);
                    break;
                }
                case "shed": {
                    element = new Shed(infoLayer);
                    break;
                }
                case "sensor": {
                    element = new Sensor(infoLayer);
                    break;
                }
                case "switch_in":
                case "switch_out": {
                    element = new Switch(infoLayer);
                    break;
                }
            }
            elements.push(element);
            networkLayer.add(element);
            state.nodes.push(element);
        }
        for (let i = 0, li = json["sections"].length; i < li; i++) {
            const pathType = json["sections"][i]["path"]["type"];
            const beginElement = elements[i];
            const endElement = elements[(i + 1) % li];
            const loopOrBridge = true;
            const section = new Section(pathType, beginElement, endElement, loopOrBridge, infoLayer);
            sections.push(section);
            networkLayer.add(section);
            state.nodes.push(section);
        }
        super(infoLayer);
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
    update(json, networkLayer, infoLayer) {
        const name = json["name"];
        const {x, y} = averagePoint(json["elements"]);
        this._name = name;
        this._x = x;
        this._y = y;
        for (let i = 0, li = this.__elements.length; i < li; i++) {
            this.__elements[i].update(json["elements"][i]);
        }
        for (let i = 0, li = this.__sections.length; i < li; i++) {
            this.__sections[i].update(json["sections"][i]);
        }
        super.update(json, null, networkLayer, infoLayer);
    }
}
