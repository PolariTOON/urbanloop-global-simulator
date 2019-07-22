import {Entity} from "./entity.js";
const {Arrow} = Konva;

const loopColor = 'rgb(156, 156, 156)';
const loopSelectedColor = 'rgb(255, 200, 20)';

const bridgeColor = 'rgb(156,63,28)';
const bridgeSelectedColor = 'rgb(255, 200, 20)';

export class Section extends Entity {
    constructor(json, startElement, endElement, loopOrBridge, infoLayer) {
        const name = json["name"];
        const x = (startElement.x() + endElement.x()) / 2;
        const y = (startElement.y() + endElement.y()) / 2;
        const label = name;
        super({
            name,
            label,
            x,
            y,
            offsetX: x,
            offsetY: y
        }, infoLayer);
        this.loopOrBridge = loopOrBridge;
        switch (json["path"]["type"]) {
            case "line":
            default: {
                this.path = new Arrow({
                    points: [startElement.x(), startElement.y(), endElement.x(), endElement.y()],
                    stroke: loopOrBridge ? loopColor : bridgeColor,
                    tension: 1,
                    strokeWidth: 2.5,
                    pointerLength : 4,
                    pointerWidth : 4
                });
                break;
            }
        }
        this.add(this.path);
        this.unselect();
    }
    select() {
        this.path.stroke(this.loopOrBridge ? loopSelectedColor : bridgeSelectedColor);
    }
    unselect() {
        this.path.stroke(this.loopOrBridge ? loopColor : bridgeColor);
    }
    scale() {
        return super.scale();
    }
}
