import {state} from "./state.js";
import {Station} from "./station.js";
import {Shed} from "./shed.js";
import {Sensor} from "./sensor.js";
import {Switch} from "./switch.js";
import {Section} from "./section.js";
import {Pod} from "./pod.js";
const {Text} = Konva;

const textColor = "#333";

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

export class Loop {
    constructor(json, networkLayer, infoLayer) {
        const name = json["name"];
        const {x, y} = averagePoint(json["elements"]);
        this.name = name;
        this.x = x;
        this.y = y;
        this.elements = [];
        this.sections = [];

        // On ajoute les éléments
        for (const elt of json["elements"]) {
            switch (elt["type"]){
                case "station": {
                    const station = new Station(elt, infoLayer);
                    this.elements.push(station);
                    networkLayer.add(station);
                    state.nodes.push(station);
                    break;
                }
                case "shed": {
                    const shed = new Shed(elt, infoLayer);
                    this.elements.push(shed);
                    networkLayer.add(shed);
                    state.nodes.push(shed);
                    break;
                }
                case "sensor": {
                    const sensor = new Sensor(elt, infoLayer);
                    this.elements.push(sensor);
                    networkLayer.add(sensor);
                    state.nodes.push(sensor);
                    break;
                }
                case "switch_in":
                case "switch_out": {
                    const sw = new Switch(elt, infoLayer);
                    this.elements.push(sw);
                    networkLayer.add(sw);
                    state.nodes.push(sw);
                    break;
                }
            }
        }

        // On ajoute les sections
        for (let i = 0, li = json["sections"].length; i < li; i++) {
            const beginElement = this.elements[i];
            const endElement = this.elements[(i + 1) % li];
            const section = new Section(json["sections"][i], beginElement, endElement, true, infoLayer);
            this.sections.push(section);
            networkLayer.add(section);
            state.nodes.push(section);
        }

        // On ajoute les capsules déjà présente sur les sections
        for (const pod of json["pods"]) {
            const p = new Pod(pod, json, null, infoLayer);
            networkLayer.add(p);
            state.pods.set(pod["id"], p);
        }

        this._text = new Text({
            x,
            y,
            text: name,
            fontFamily: "Georgia, Times, serif",
            fontVariant: "small-caps",
            fontSize: 20,
            fill: textColor,
        });
        this._text.offsetX(this._text.width() / 2);
        this._text.offsetY(this._text.height() / 2);

        infoLayer.add(this._text);
        state.labels.push(this._text);
    }
    update(json, networkLayer, infoLayer) {
        for (let i = 0, li = this.elements.length; i < li; i++) {
            this.elements[i].update(json["elements"][i]);
        }
        for (let i = 0, li = this.sections.length; i < li; i++) {
            this.sections[i].update(json["sections"][i]);
        }
        for (const pod of json["pods"]) {
            if (state.pods.has(pod["id"])) {
                const p = state.pods.get(pod["id"]);
                p.update(pod, json, null);
                p.keepFlag = 1;
            } else {
                const p = new Pod(pod, json, null, infoLayer);
                p.keepFlag = 2;
                networkLayer.add(p);
                state.pods.set(pod["id"], p);
            }
        }
    }
}
