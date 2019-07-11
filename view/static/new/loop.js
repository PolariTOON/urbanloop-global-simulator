import {appState, networkLayer, getNetworkDivSize   } from "./network.js";
import {Station} from "./station.js";
import {Shed} from "./shed.js";
import {Sensor} from "./sensor.js";
import {Switch} from "./switch.js";

const loopColor = 'rgb(156, 156, 156)';
const loopSelectedColor = 'rgb(255, 200, 20)';

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

        for (const elt of loopJSON["elements"]){
            switch (elt["type"]){
                case "station":
                    new Station(elt);
                    break;
                case "shed":
                    new Shed(elt);
                    break;
                case "sensor":
                    new Sensor(elt);
                    break;
                case "switch_in":
                case "switch_out":
                    new Switch(elt);
                    break;
            }
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

        //initBehaviors(this, this.innerCircle, this.outerCircle);
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
        const y = getNetworkDivSize().height - this.averageY;
        this.text.y(y);
    }

    updateScale(value) {
        this.text.scaleX(value);
        this.text.scaleY(value);
    }
}

