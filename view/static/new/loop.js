import {appState, networkLayer, getNetworkDivSize} from "./network.js";
import {Station} from "./station.js";
import {Shed} from "./shed.js";
import {Sensor} from "./sensor.js";
import {Switch} from "./switch.js";
import {Section} from "./section.js";
import {Pod} from "./pod.js";

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
    constructor(loopJSON) {
        this.json = loopJSON;
        const averagePointLoop = averagePoint(loopJSON["elements"]);
        this.averageX = averagePointLoop[0];
        this.averageY = getNetworkDivSize().height - averagePointLoop[1];
        this.name = loopJSON["name"];
        this.elements = [];

        // On ajoute les éléments
        for (const elt of loopJSON["elements"]){
            switch (elt["type"]){
                case "station":
                    const station = new Station(elt);
                    this.elements.push(station);
                    break;
                case "shed":
                    const shed = new Shed(elt);
                    this.elements.push(shed);
                    break;
                case "sensor":
                    const sensor = new Sensor(elt);
                    this.elements.push(sensor);
                    break;
                case "switch_in":
                case "switch_out":
                    const sw = new Switch(elt);
                    this.elements.push(sw);
                    break;
            }
        }

        // On ajoute les sections
        const loopSize = loopJSON["sections"].length;
        for (let section = 0; section < loopSize; section++){
            const beginElement = this.elements[section];
            const endElement = this.elements[(section + 1) % loopSize];
            new Section(loopJSON["sections"][section], beginElement, endElement);
        }

        // On ajoute les capsules déjà présente sur les sections
        for (const pod of loopJSON["pods"]){
            new Pod(pod, loopJSON, false);
        }

        this.text = new Konva.Text({
            name: this.name,
            x: this.averageX,
            y: this.averageY,
            text: loopJSON["name"],
            fontFamily: "Georgia, serif",
            fontSize: 20,
            fontVariant: "small-caps",
            fill: "black"
        });
        this.text.offsetX(this.text.width() / 2);
        this.text.offsetY(this.text.height() / 2);

        networkLayer.add(this.text);
        appState.objects.push(this);
    }

    select() {
        if (appState.selectedObject !== undefined && appState.selectedObject !== this) {
            appState.selectedObject.unselect();
        }
        appState.selectedObject = this;
        networkLayer.batchDraw();
    }

    unselect() {
        if (appState.selectedObject === this) {
            appState.selectedObject = undefined;
        }
        networkLayer.batchDraw();
    }

    updatePosition() {
        const y = this.averageY;
        this.text.y(y);
    }

    updateScale(value) {
        this.text.scaleX(value);
        this.text.scaleY(value);
    }
}
