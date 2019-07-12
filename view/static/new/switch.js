import {appState, networkLayer, infoLayer, getNetworkDivSize, initBehaviors} from "./network.js";

const switchColor = 'rgb(200, 40, 40)';
const switchSelectedColor = 'rgb(255, 200, 20)';

export class Switch {
    constructor(switchJSON, switchRadius = 12, switchWidth = 4) {
        this.json = switchJSON;
        this.name = switchJSON["name"];

        this.x = switchJSON['x'];
        this.y = getNetworkDivSize().height - switchJSON['y'];
        const semiWidth = Math.floor(switchWidth / 2);

        this.innerCircle = new Konva.Circle({
            x: this.x,
            y: this.y,
            radius: switchRadius - semiWidth,
            fill: 'white',
            stroke: 'black',
            strokeWidth: 0.3,
        });

        this.outerCircle = new Konva.Circle({
            name: this.name,
            x: this.x,
            y: this.y,
            radius: switchRadius + semiWidth,
            fill: switchColor,
            stroke: 'black',
            strokeWidth: 0.3,
        });

        this.info = new Konva.Label({
            x: this.x,
            y: this.y,
            opacity: 0.75,
            visible: false,
            listening: false
        });

        this.info.add(new Konva.Tag({
            fill: 'black',
            pointerDirection: 'down',
            pointerWidth: 10,
            pointerHeight: 10,
            lineJoin: 'round',
            shadowColor: 'black',
            shadowBlur: 10,
            shadowOffset: 10,
            shadowOpacity: 0.2
        }));

        this.info.add(
            new Konva.Text({
                text: switchJSON['name'],
                fontFamily: 'Calibri',
                fontSize: 18,
                padding: 5,
                fill: 'white'
            })
        );

        initBehaviors(this, this.innerCircle, this.outerCircle, this.info);

        networkLayer.add(this.outerCircle);
        networkLayer.add(this.innerCircle);
        infoLayer.add(this.info);

        appState.objects.push(this);
    }

    select() {
        if (appState.selectedObject !== undefined && appState.selectedObject !== this) {
            appState.selectedObject.unselect();
        }

        appState.selectedObject = this;
        this.outerCircle.fill(switchSelectedColor);
        networkLayer.batchDraw();
    }

    unselect() {
        if (appState.selectedObject === this) {
            appState.selectedObject = undefined;
        }
        this.outerCircle.fill(switchColor);
        networkLayer.batchDraw();
    }

    updatePosition() {
        const height = getNetworkDivSize().height;
        const y = height - this.json['y'];
        this.innerCircle.y(y);
        this.outerCircle.y(y);
        this.info.y(y);
    }

    updateScale(value) {
        this.innerCircle.scaleX(value);
        this.innerCircle.scaleY(value);
        this.outerCircle.scaleX(value);
        this.outerCircle.scaleY(value);
        this.info.scaleX(value);
        this.info.scaleY(value);
    }
}

export function updateSwitchFromJSON(switchJSON) {

}