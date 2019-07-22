import {appState} from "./network.js";
const {Circle, Group, Label, Rect, Tag, Text} = Konva;


const stationColor = "rgb(40, 40, 200)";
const stationSelectedColor = "rgb(255, 200, 20)";

export class Station extends Group {
    constructor(json, infoLayer) {
        const name = json["name"];
        const x = json["x"];
        const y = json["y"];
        const stationRadius = 12;
        const stationWidth = 4;
        const dockSize = 24;
        const semiWidth = Math.floor(stationWidth / 2);
        super({
            name,
            x,
            y,
            offsetX: x,
            offsetY: y
        });

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

        this.info = new Label({
            x,
            y,
            opacity: 0.75,
            visible: false,
            listening: false
        });

        this.info.add(
            new Tag({
                fill: "black",
                pointerDirection: "down",
                pointerWidth: 10,
                pointerHeight: 10,
                lineJoin: "round",
                shadowColor: "black",
                shadowBlur: 10,
                shadowOffset: 10,
                shadowOpacity: 0.2
            })
        );

        this.info.add(
            new Text({
                text: "Station : " + json["name"] + " | Capacity : " + json["pods"]["max"],
                fontFamily: "Calibri",
                fontSize: 18,
                padding: 5,
                fill: "white"
            })
        );

        this.add(this.outerCircle);
        this.add(this.innerCircle);
        this.dockList.forEach(dock => {
            this.add(dock);
            dock.hide();
        });
        infoLayer.add(this.info);

        appState.objects.push(this);
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

    updateScale(value) {
        this.innerCircle.scaleX(value);
        this.innerCircle.scaleY(value);
        this.outerCircle.scaleX(value);
        this.outerCircle.scaleY(value);
        this.dockList.forEach(dock => {
            dock.scaleX(value);
            dock.scaleY(value);
        });
        this.info.scaleX(value);
        this.info.scaleY(value);

    }
}

export function updateStationFromJSON(json) {
    let targetStations = appState.objects.filter(station => station.uuid.includes(json["uuid"]));
    targetStations.forEach(station => station.update(json));
}
