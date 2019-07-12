import {appState, networkLayer, infoLayer, getNetworkDivSize, initBehaviors} from "./network.js";

const shedColor = 'rgb(40, 40, 40)';
const shedSelectedColor = 'rgb(255, 200, 20)';

export class Shed {
    constructor(shedJSON, shedRadius = 12, shedWidth = 4) {
        this.json = shedJSON;
        this.name = shedJSON["name"];

        this.x = shedJSON['x'];
        this.y = getNetworkDivSize().height - shedJSON['y'];
        const semiWidth = Math.floor(shedWidth / 2);

        this.innerRectangle = new Konva.Rect({
            name: this.name,
            x: this.x,
            y: this.y,
            width: 2 * (shedRadius - semiWidth),
            height: 2 * (shedRadius - semiWidth),
            fill: 'white',
            stroke: 'black',
            strokeWidth: 0.3,
        });
        this.innerRectangle.offsetX(this.innerRectangle.width() / 2);
        this.innerRectangle.offsetY(this.innerRectangle.height() / 2);

        this.outerRectangle = new Konva.Rect({
            name: this.name,
            x: this.x,
            y: this.y,
            width: 2 * (shedRadius + semiWidth),
            height: 2 * (shedRadius + semiWidth),
            fill: shedColor,
            stroke: 'black',
            strokeWidth: 0.3,
        });
        this.outerRectangle.offsetX(this.outerRectangle.width() / 2);
        this.outerRectangle.offsetY(this.outerRectangle.height() / 2);

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
                text: 'Shed : ' + shedJSON['name'] + ' | Capacity : ' + shedJSON['pods']["max"],
                fontFamily: 'Calibri',
                fontSize: 18,
                padding: 5,
                fill: 'white'
            })
        );

        initBehaviors(this, this.innerRectangle, this.outerRectangle, this.info);

        networkLayer.add(this.outerRectangle);
        networkLayer.add(this.innerRectangle);
        infoLayer.add(this.info);

        appState.objects.push(this);
    }

    select() {
        if (appState.selectedObject !== undefined && appState.selectedObject !== this) {
            appState.selectedObject.unselect();
        }

        appState.selectedObject = this;
        this.outerRectangle.fill(shedSelectedColor);
        networkLayer.batchDraw();
    }

    unselect() {
        if (appState.selectedObject === this) {
            appState.selectedObject = undefined;
        }
        this.outerRectangle.fill(shedColor);
        networkLayer.batchDraw();
    }

    updatePosition() {
        const y = getNetworkDivSize().height - this.y;
        this.innerRectangle.y(y);
        this.outerRectangle.y(y);
        this.info.y(y);
    }

    updateScale(value) {
        this.innerRectangle.scaleX(value);
        this.innerRectangle.scaleY(value);
        this.outerRectangle.scaleX(value);
        this.outerRectangle.scaleY(value);
        this.info.scaleX(value);
        this.info.scaleY(value);
    }

    update(shedJSON) {
        this.json = shedJSON;
    }
}

export function updateShedFromJSON(shedJSON) {
    let targetSheds = appState.objects.filter(shed => shed.uuid.includes(shedJSON['uuid']));
    targetSheds.forEach(shed => shed.update(shedJSON));
}