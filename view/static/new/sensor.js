import {appState} from "./network.js";
const {Group, Label, Star, Tag, Text} = Konva;

const sensorColor = 'rgb(40,158,0)';
const sensorSelectedColor = 'rgb(255, 200, 20)';

export class Sensor extends Group {
    constructor(json, infoLayer) {
        const name = json["name"];
        const x = json["x"];
        const y = json["y"];
        const sensorRadius = 18;
        super({
            name,
            x,
            y,
            offsetX: x,
            offsetY: y
        });

        this.star = new Star({
            x,
            y,
            numPoints: 5,
            innerRadius: sensorRadius / 2,
            outerRadius: sensorRadius,
            fill: sensorColor,
            stroke: 'black',
            strokeWidth: 0.3
      });

        this.info = new Label({
            x,
            y,
            opacity: 0.75,
            visible: false,
            listening: false
        });

        this.info.add(
            new Tag({
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
            new Text({
                text: name,
                fontFamily: 'Calibri',
                fontSize: 18,
                padding: 5,
                fill: 'white'
            })
        );

        this.add(this.star);
        infoLayer.add(this.info);

        appState.objects.push(this);
    }

    select() {
        this.star.fill(sensorSelectedColor);
    }

    unselect() {
        this.star.fill(sensorColor);
    }

    updateScale(value) {
        this.star.scaleX(value);
        this.star.scaleY(value);
        this.info.scaleX(value);
        this.info.scaleY(value);
    }

}

export function updateSensorFromJSON(sensorJSON) {
    let targetSensor = appState.objects.filter(sensor => sensor.name.includes(sensorJSON["name"]));
    targetSensor.forEach(sensor => sensor.update(sensorJSON));
}
