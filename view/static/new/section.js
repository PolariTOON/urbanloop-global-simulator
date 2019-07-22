const {Arrow, Group, Label, Tag, Text} = Konva;

const loopColor = 'rgb(156, 156, 156)';
const loopSelectedColor = 'rgb(255, 200, 20)';

const bridgeColor = 'rgb(156,63,28)';
const bridgeSelectedColor = 'rgb(255, 200, 20)';

export class Section extends Group {
    constructor(json, startElement, endElement, loopOrBridge, infoLayer) {
        const name = json["name"];
        const x = (startElement.x() + endElement.x()) / 2;
        const y = (startElement.y() + endElement.y()) / 2;
        super({
            name,
            x,
            y,
            offsetX: x,
            offsetY: y
        });
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
                fontSize: 9,
                padding: 5,
                fill: 'white'
            })
        );

        this.add(this.path);
        infoLayer.add(this.info);
    }

    select() {
        this.path.stroke(this.loopOrBridge ? loopSelectedColor : bridgeSelectedColor);
    }

    unselect() {
        this.path.stroke(this.loopOrBridge ? loopColor : bridgeColor);
    }
}
