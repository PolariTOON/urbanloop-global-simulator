import {Entity} from "./entity.js";
const {Rect} = Konva;

const shedColor = 'rgb(40, 40, 40)';
const shedSelectedColor = 'rgb(255, 200, 20)';

export class Shed extends Entity {
    constructor(json, infoLayer) {
        const name = json["name"];
        const x = json["x"];
        const y = json["y"];
        const shedRadius = 12;
        const shedWidth = 4;
        const semiWidth = Math.floor(shedWidth / 2);
        const innerSize = 2 * (shedRadius - semiWidth);
        const outerSize = 2 * (shedRadius + semiWidth);
        const label = 'Shed : ' + json['name'] + ' | Capacity : ' + json['pods']["max"];
        super({
            name,
            label,
            x,
            y,
            offsetX: x,
            offsetY: y
        }, infoLayer);
        this.innerRectangle = new Rect({
            x: x,
            y: y,
            width: innerSize,
            height: innerSize,
            offsetX: innerSize / 2,
            offsetY: innerSize / 2,
            fill: 'white',
            stroke: 'black',
            strokeWidth: 0.3,
        });
        this.outerRectangle = new Rect({
            x: x,
            y: y,
            width: outerSize,
            height: outerSize,
            offsetX: outerSize / 2,
            offsetY: outerSize / 2,
            fill: shedColor,
            stroke: 'black',
            strokeWidth: 0.3,
        });
        this.add(this.outerRectangle);
        this.add(this.innerRectangle);
        this.unselect();
    }
    select() {
        this.outerRectangle.fill(shedSelectedColor);
    }
    unselect() {
        this.outerRectangle.fill(shedColor);
    }
}
