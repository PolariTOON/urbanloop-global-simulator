import {appState} from "./network.js";
const {Circle, Group, Label, Tag, Text} = Konva;

const switchColor = 'rgb(200, 40, 40)';
const switchSelectedColor = 'rgb(255, 200, 20)';

export class Switch extends Group {
    constructor(json, infoLayer) {
        const name = json["name"];
        const x = json["x"];
        const y = json["y"];
        const switchRadius = 12;
        const switchWidth = 4;
        const semiWidth = Math.floor(switchWidth / 2);
        super({
            name,
            x,
            y,
            offsetX: x,
            offsetY: y
        });

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

        this.info = new Label({
            x,
            y,
            opacity: 0.75,
            visible: false,
            listening: false
        });

        this.info.add(new Tag({
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
            new Text({
                text: json['name'],
                fontFamily: 'Calibri',
                fontSize: 18,
                padding: 5,
                fill: 'white'
            })
        );

        this.add(this.outerCircle);
        this.add(this.innerCircle);
        infoLayer.add(this.info);

        appState.objects.push(this);
    }

    select() {
        this.outerCircle.fill(switchSelectedColor);
    }

    unselect() {
        this.outerCircle.fill(switchColor);
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

export function updateSwitchFromJSON(json) {

}
