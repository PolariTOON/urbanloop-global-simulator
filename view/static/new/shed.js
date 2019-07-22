import {appState} from "./network.js";
const {Group, Label, Rect, Tag, Text} = Konva;

const shedColor = 'rgb(40, 40, 40)';
const shedSelectedColor = 'rgb(255, 200, 20)';

export class Shed extends Group {
    constructor(json, infoLayer) {
        const name = json["name"];
        const x = json["x"];
        const y = json["y"];
        const shedRadius = 12;
        const shedWidth = 4;
        const semiWidth = Math.floor(shedWidth / 2);
        const innerSize = 2 * (shedRadius - semiWidth);
        const outerSize = 2 * (shedRadius + semiWidth);
        super({
            name,
            x,
            y,
            offsetX: x,
            offsetY: y
        });

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
                text: 'Shed : ' + json['name'] + ' | Capacity : ' + json['pods']["max"],
                fontFamily: 'Calibri',
                fontSize: 18,
                padding: 5,
                fill: 'white'
            })
        );

        this.add(this.outerRectangle);
        this.add(this.innerRectangle);
        infoLayer.add(this.info);

        appState.objects.push(this);
    }

    select() {
        this.outerRectangle.fill(shedSelectedColor);
    }

    unselect() {
        this.outerRectangle.fill(shedColor);
    }

    updateScale(value) {
        this.innerRectangle.scaleX(value);
        this.innerRectangle.scaleY(value);
        this.outerRectangle.scaleX(value);
        this.outerRectangle.scaleY(value);
        this.info.scaleX(value);
        this.info.scaleY(value);
    }
}

export function updateShedFromJSON(json) {
    let targetSheds = appState.objects.filter(shed => shed.uuid.includes(json['uuid']));
    targetSheds.forEach(shed => shed.update(json));
}
