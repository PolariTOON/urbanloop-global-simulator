import {state} from "./state.js";
import {Legend} from "./legend.js";
import {Pod} from "./pod.js";
import {Sensor} from "./sensor.js";
import {Shed} from "./shed.js";
import {Station} from "./station.js";
import {Switch} from "./switch.js";
//p_tb debut
import {HangarSimple} from "./HangarSimple.js";
import {HangarRevision} from "./HangarRevision.js";
//p_tb fin
const {Group} = Konva;

export class Line extends Group {
    // __legend;
    // __name;
    // __elements;
    // __sections;
    // __x;
    // __y;
    constructor(elementsJSON, legendsLayer, elementsLayer, sectionsLayer, hintsLayer) {
        const text = new Legend();
        const elements = [];
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
                //p_tb debut
                case "HangarSimple":{
                	element = new HangarSimple(hintsLayer);
                	break;
                }
                case "HangarRevision":{
                	element = new HangarRevision(hintsLayer);
                	break;
                }
                //p_tb fin
            }
            elements.push(element);
            //console.log(element);//p_tb
            elementsLayer.add(element);
            state.nodes.push(element);
        }
        super();
        legendsLayer.add(text);
        this.__legend = text;
        this.__legend.hide();
        this.__elements = elements;
        this.__sections = [];
    }
    set _name(value) {
        this.__name = value;
        this.__legend._name = value;
    }
    get _name() {
        return this.__name;
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
    update(json, loopsJSON, elementsJSON, sectionsJSON, podsLayer, hintsLayer, showWaitingTravelers) {
        // pods
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
        // elements
        for (let i = 0, li = elementsJSON.length; i < li; i++) {
            if (this.__elements[i] instanceof Switch) {
                this.__elements[i].update(elementsJSON[i], podsLayer, hintsLayer);
            } 
            else if (this.__elements[i] instanceof Station) {
                this.__elements[i].update(elementsJSON[i], showWaitingTravelers);
            }
            else {
                this.__elements[i].update(elementsJSON[i]);
            }
        }
        // sections
        for (let i = 0, li = sectionsJSON.length; i < li; i++) {
            this.__sections[i].update(sectionsJSON[i]);
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
