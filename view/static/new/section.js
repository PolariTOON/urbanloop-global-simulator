import {appState, setCursor, infoLayer, networkLayer} from "./network.js";

const sectionColor = 'rgb(156, 156, 156)';
const sectionSelectedColor = 'rgb(255, 200, 20)';

function drawLine(beginElement, endElement) {
    return new Konva.Arrow({
        points: [beginElement.x, beginElement.y, endElement.x, endElement.y],
        stroke: sectionColor,
        tension: 1,
        strokeWidth: 2.5,
        pointerLength : 4,
        pointerWidth : 4
    });
}

export class Section {
    constructor(sectionJSON, beginElement, endElement){
        this.name = sectionJSON["name"];
        this.beginElement = beginElement;
        this.endElement = endElement;
        this.pathType = sectionJSON["path"]["type"];
        this.x = (this.beginElement.x + this.endElement.x)/2;
        this.y = (this.beginElement.y + this.endElement.y) / 2;

        switch (this.pathType){
            case "line":
            default:
                this.line = drawLine(this.beginElement, this.endElement);
                break;
        }

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

        this.line.on('mouseenter', () => {
            setCursor("pointer");
            this.info.show();
            infoLayer.batchDraw();
        });

        this.line.on('mouseleave', () => {
            setCursor("auto");
            this.info.hide();
            infoLayer.batchDraw();
        });

        this.line.on('mousedown', () => {
        this.select();
    });

        networkLayer.add(this.line);
        infoLayer.add(this.info);
    }

    select() {
        if (appState.selectedObject !== undefined && appState.selectedObject !== this) {
            appState.selectedObject.unselect();
        }

        appState.selectedObject = this;
        this.line.stroke(sectionSelectedColor);
        networkLayer.batchDraw();
    }

    unselect() {
        if (appState.selectedObject === this) {
            appState.selectedObject = undefined;
        }
        this.line.stroke(sectionColor);
        networkLayer.batchDraw();
    }

    update(sectionJSON) {
        this.json = sectionJSON;
    }
}
