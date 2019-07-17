import {appState, networkLayer, infoLayer, initBehaviors} from "./network.js";

const sensorColor = 'rgb(40,158,0)';
const sensorSelectedColor = 'rgb(255, 200, 20)';

export class Sensor {
    constructor(sensorJSON, sensorRadius = 18) {
        this.json = sensorJSON;
        this.name = sensorJSON["name"];
        this.x = sensorJSON["x"];
        this.y = sensorJSON["y"];

        this.star = new Konva.Star({
            name: this.name,
            x: this.x,
            y: this.y,
            numPoints: 5,
            innerRadius: sensorRadius / 2,
            outerRadius: sensorRadius,
            fill: sensorColor,
            stroke: 'black',
            strokeWidth: 0.3
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
                fontSize: 18,
                padding: 5,
                fill: 'white'
            })
        );

        initBehaviors(this, this.star, undefined, this.info);

        networkLayer.add(this.star);
        infoLayer.add(this.info);

        appState.objects.push(this);
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
