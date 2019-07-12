import {appState, networkLayer, infoLayer, getNetworkDivSize, initBehaviors} from "./network.js";

const sensorColor = 'rgb(255,24,231)';
const sensorSelectedColor = 'rgb(255, 200, 20)';

export class Sensor {
    constructor(sensorJSON, sensorRadius = 12) {
        this.json = sensorJSON;
        this.name = sensorJSON["name"];
        this.x = sensorJSON["x"];
        const x = this.x;
        this.y = sensorJSON["y"];
        const y = getNetworkDivSize().height - this.y;

        this.star = new Konva.Star({
            name: this.name,
            x: x,
            y: y,
            numPoints: 5,
            innerRadius: sensorRadius / 2,
            outerRadius: sensorRadius,
            fill: sensorColor,
            stroke: 'black',
            strokeWidth: 0.3
      });

        this.info = new Konva.Label({
            x: x,
            y: y,
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
                text: "Sensor",
                fontFamily: 'Calibri',
                fontSize: 18,
                padding: 5,
                fill: 'white'
            })
        );

        initBehaviors(this, this.star, undefined, this.info);

        networkLayer.add(this.star);
        infoLayer.add(this.info);

        appState.objects.push(this);
        console.log("xy:" + this.x + " " + this.y)
    }

    select() {
        if (appState.selectedObject !== undefined && appState.selectedObject !== this) {
            appState.selectedObject.unselect();
        }

        appState.selectedObject = this;
        this.star.fill(sensorSelectedColor);
        networkLayer.batchDraw();
    }

    unselect() {
        if (appState.selectedObject === this) {
            appState.selectedObject = undefined;
        }
        this.star.fill(sensorColor);
        networkLayer.batchDraw();
    }

    updatePosition() {
        const y = getNetworkDivSize().height - this.y;
        this.star.y(y);
        this.info.y(y);
    }

    updateScale(value) {
        this.star.scaleX(value);
        this.star.scaleY(value);
        this.info.scaleX(value);
        this.info.scaleY(value);
    }

    update(sensorJSON) {
        this.json = sensorJSON;
    }

}

export function updateSensorFromJSON(sensorJSON) {
    let targetSensor = appState.objects.filter(sensor => sensor.name.includes(sensorJSON["name"]));
    targetSensor.forEach(sensor => sensor.update(sensorJSON));
}