import {appState, handCursor, infoLayer, moveCursor, networkLayer} from "./network.js";
import {Pod} from "./pod.js";

const bridgeColor = 'rgb(156,63,28)';
const bridgeSelectedColor = 'rgb(255, 200, 20)';

export class Bridge{
    constructor(bridgeJSON, switchIn, switchOut, loopsJSON){
        this.json = bridgeJSON;
        this.section = bridgeJSON["section"];
        this.name = bridgeJSON["name"];
        this.switchIn = switchIn;
        this.switchOut = switchOut;
        this.x = (this.switchIn.x + this.switchOut.x) / 2;
        this.y = (this.switchIn.y + this.switchOut.y) / 2;

        this.line = new Konva.Arrow({
            points: [switchOut.x, switchOut.y, switchIn.x, switchIn.y],
            stroke: bridgeColor,
            tension: 1,
            strokeWidth: 2.5,
            pointerLength : 4,
            pointerWidth : 4
        });

        this.info = new Konva.Label({
            x: this.x,
            y: this.y,
            opacity: 0.75,
            visible: false,
            listening: false
        });

        this.info.add(
            new Konva.Tag({
                fill: 'black',
                pointerDirection: 'down',
                pointerWidth: 10,
                pointerHeight: 10,
                lineJoin: 'round',
                shadowColor: 'black',
                shadowBlur: 10,
                shadowOffset: 10,
                shadowOpacity: 0.2
            })
        );

        this.info.add(
            new Konva.Text({
                text: this.name,
                fontFamily: 'Calibri',
                fontSize: 9,
                padding: 5,
                fill: 'white'
            })
        );

        this.line.on('mouseover', () => {
            handCursor();
            this.info.show();
            infoLayer.batchDraw();
        });

        this.line.on('mouseout', () => {
            moveCursor();
            this.info.hide();
            infoLayer.batchDraw();
        });

        this.line.on('mousedown', () => {
        this.select();
        });

        networkLayer.add(this.line);
        infoLayer.add(this.info);

        for (const pod of bridgeJSON["pods"]){
            new Pod(pod, bridgeJSON, false, loopsJSON);
        }

    }

    select() {
        if (appState.selectedObject !== undefined && appState.selectedObject !== this) {
            appState.selectedObject.unselect();
        }

        appState.selectedObject = this;
        this.line.stroke(bridgeSelectedColor);
        networkLayer.batchDraw();
    }

    unselect() {
        if (appState.selectedObject === this) {
            appState.selectedObject = undefined;
        }
        this.line.stroke(bridgeColor);
        networkLayer.batchDraw();
    }

    update(bridgeJSON) {
        this.json = bridgeJSON;
    }
}
