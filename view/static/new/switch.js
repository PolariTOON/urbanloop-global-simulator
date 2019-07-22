import {Entity} from "./entity.js";
const {Circle} = Konva;

const switchColor = 'rgb(200, 40, 40)';
const switchSelectedColor = 'rgb(255, 200, 20)';

export class Switch extends Entity {
    constructor(json, infoLayer) {
        const name = json["name"];
        const x = json["x"];
        const y = json["y"];
        const switchRadius = 12;
        const switchWidth = 4;
        const semiWidth = Math.floor(switchWidth / 2);
        const label = name;
        super({
            name,
            label,
            x,
            y,
            offsetX: x,
            offsetY: y
        }, infoLayer);
        this.innerCircle = new Circle({
            x,
            y,
            radius: switchRadius - semiWidth,
            fill: 'white',
            stroke: 'black',
            strokeWidth: 0.3,
        });
        this.outerCircle = new Circle({
            x,
            y,
            radius: switchRadius + semiWidth,
            fill: switchColor,
            stroke: 'black',
            strokeWidth: 0.3,
        });
        this.add(this.outerCircle);
        this.add(this.innerCircle);
    }
    select() {
        this.outerCircle.fill(switchSelectedColor);
    }
    unselect() {
        this.outerCircle.fill(switchColor);
    }
}
