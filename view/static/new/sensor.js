import {Entity} from "./entity.js";
const {Star} = Konva;

const sensorColor = 'rgb(40,158,0)';
const sensorSelectedColor = 'rgb(255, 200, 20)';

export class Sensor extends Entity {
    constructor(json, infoLayer) {
        const name = json["name"];
        const x = json["x"];
        const y = json["y"];
        const sensorRadius = 18;
        const label = name;
        super({
            name,
            label,
            x,
            y,
            offsetX: x,
            offsetY: y
        }, infoLayer);
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
        this.add(this.star);
        this.unselect();
    }
    select() {
        this.star.fill(sensorSelectedColor);
    }
    unselect() {
        this.star.fill(sensorColor);
    }
}
