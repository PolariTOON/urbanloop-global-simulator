import {Entity} from "./entity.js";
const {Circle, Rect} = Konva;

const stationColor = "rgb(40, 40, 200)";
const stationSelectedColor = "rgb(255, 200, 20)";

export class Station extends Entity {
    constructor(json, infoLayer) {
        const name = json["name"];
        const x = json["x"];
        const y = json["y"];
        const stationRadius = 12;
        const stationWidth = 4;
        const dockSize = 24;
        const semiWidth = Math.floor(stationWidth / 2);
        const label = "Station : " + json["name"] + " | Capacity : " + json["pods"]["max"];
        super({
            name,
            label,
            x,
            y,
            offsetX: x,
            offsetY: y
        }, infoLayer);
        this.capacity = json["capacity"];
        this.stationRadius = stationRadius;
        this.dockSize = dockSize;
        this.innerCircle = new Circle({
            x,
            y,
            radius: stationRadius - semiWidth,
            fill: "white",
            stroke: "black",
            strokeWidth: 0.3,
        });
        this.outerCircle = new Circle({
            x,
            y,
            radius: stationRadius + semiWidth,
            fill: stationColor,
            stroke: "black",
            strokeWidth: 0.3,
        });
        this.dockList = [];
        for (let i = 0; i < this.capacity; i++) {
            let dockRect = new Rect({
                x: x + 10 * stationRadius + (6 * i + 2) * dockSize,
                y: y,
                width: dockSize,
                height: dockSize,
                fill: "white",
                stroke: "black",
                strokeWidth: 1,
            });
            dockRect.offsetX(dockRect.width() / 2);
            dockRect.offsetY(dockRect.height() / 2);
            this.dockList.push(dockRect);
        }
        this.add(this.outerCircle);
        this.add(this.innerCircle);
        for (const dock of this.dockList) {
            this.add(dock);
        }
        this.unselect();
    }
    select() {
        this.outerCircle.fill(stationSelectedColor);

        this.dockList.forEach(dock => {
            dock.show();
        });
    }
    unselect() {
        this.outerCircle.fill(stationColor);

        this.dockList.forEach(dock => {
            dock.hide();
        });
    }
}
