import {appState} from "./network.js";
import {Station} from "./station.js";
import {Shed} from "./shed.js";
import {Sensor} from "./sensor.js";
import {Switch} from "./switch.js";
import {Section} from "./section.js";
import {Pod} from "./pod.js";
const {Text} = Konva;

function averagePoint(elements){
    let x = 0;
    let y = 0;
    for (const elt of elements){
        x += elt["x"];
        y += elt["y"];
    }
    x /= elements.length;
    y /= elements.length;
    return [x, y];
}

export class Loop {
    constructor(json, networkLayer, infoLayer) {
        const name = json["name"];
        const averagePointLoop = averagePoint(json["elements"]);
        const x = averagePointLoop[0];
        const y = averagePointLoop[1];
        this.name = name;
        this.x = x;
        this.y = y;
        this.elements = [];

        // On ajoute les éléments
        for (const elt of json["elements"]) {
            switch (elt["type"]){
                case "station": {
                    const station = new Station(elt, infoLayer);
                    this.elements.push(station);
                    networkLayer.add(station);
                    appState.objects.push(station);
                    break;
                }
                case "shed": {
                    const shed = new Shed(elt, infoLayer);
                    this.elements.push(shed);
                    networkLayer.add(shed);
                    appState.objects.push(shed);
                    break;
                }
                case "sensor": {
                    const sensor = new Sensor(elt, infoLayer);
                    this.elements.push(sensor);
                    networkLayer.add(sensor);
                    appState.objects.push(sensor);
                    break;
                }
                case "switch_in":
                case "switch_out": {
                    const sw = new Switch(elt, infoLayer);
                    this.elements.push(sw);
                    networkLayer.add(sw);
                    appState.objects.push(sw);
                    break;
                }
            }
        }

        // On ajoute les sections
        for (let i = 0, li = json["sections"].length; i < li; i++) {
            const beginElement = this.elements[i];
            const endElement = this.elements[(i + 1) % li];
            const section = new Section(json["sections"][i], beginElement, endElement, true, infoLayer);
            networkLayer.add(section);
            appState.objects.push(section);
        }

        // On ajoute les capsules déjà présente sur les sections
        for (const pod of json["pods"]) {
            const p = new Pod(pod, json, false, null, infoLayer);
            networkLayer.add(p);
            appState.objects.push(p);
        }

        this.text = new Text({
            x,
            y,
            text: name,
            fontFamily: "Georgia, serif",
            fontSize: 20,
            fontVariant: "small-caps",
            fill: "black"
        });
        this.text.offsetX(this.text.width() / 2);
        this.text.offsetY(this.text.height() / 2);

        infoLayer.add(this.text);
    }
}
