import {appState, networkLayer, infoLayer, getNetworkDivSize, initBehaviors} from "./network.js";

const stationColor = "rgb(40, 40, 200)";
const stationSelectedColor = "rgb(255, 200, 20)";

export class Station {
    constructor(stationJSON, stationRadius = 12, stationWidth = 4, dockSize = 24) {
        this.json = stationJSON;
        this.capacity = stationJSON["capacity"];
        this.stationRadius = stationRadius;
        this.dockSize = dockSize;
        this.name = stationJSON["name"];
        this.x = stationJSON["x"];
        this.y = getNetworkDivSize().height - stationJSON["y"];

        const semiWidth = Math.floor(stationWidth / 2);

        this.innerCircle = new Konva.Circle({
            name: this.uuid,
            x: this.x,
            y: this.y,
            radius: stationRadius - semiWidth,
            fill: "white",
            stroke: "black",
            strokeWidth: 0.3,
        });

        this.outerCircle = new Konva.Circle({
            name: this.uuid,
            x: this.x,
            y: this.y,
            radius: stationRadius + semiWidth,
            fill: stationColor,
            stroke: "black",
            strokeWidth: 0.3,
        });

        this.dockList = [];
        for (let i = 0; i < this.capacity; i++) {
            let dockRect = new Konva.Rect({
                name: this.name,
                x: this.x + 10 * stationRadius + (6 * i + 2) * dockSize,
                y: this.y,
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

        this.info = new Konva.Label({
            x: this.x,
            y: this.y,
            opacity: 0.75,
            visible: false,
            listening: false
        });

        this.info.add(
            new Konva.Tag({
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
            new Konva.Text({
                text: "Station : " + stationJSON["name"] + " | Capacity : " + stationJSON["pods"]["max"],
                fontFamily: "Calibri",
                fontSize: 18,
                padding: 5,
                fill: "white"
            })
        );

        initBehaviors(this, this.innerCircle, this.outerCircle, this.info);

        networkLayer.add(this.outerCircle);
        networkLayer.add(this.innerCircle);
        this.dockList.forEach(dock => {
            networkLayer.add(dock);
            dock.hide();
        });
        infoLayer.add(this.info);

        appState.objects.push(this);
    }

    select() {
        if (appState.selectedObject !== undefined && appState.selectedObject !== this) {
            appState.selectedObject.unselect();
        }

        appState.selectedObject = this;
        this.outerCircle.fill(stationSelectedColor);

        this.dockList.forEach(dock => {
            dock.show();
        });

        networkLayer.batchDraw();
    }

    unselect() {
        if (appState.selectedObject === this) {
            appState.selectedObject = undefined;
        }
        this.outerCircle.fill(stationColor);

        this.dockList.forEach(dock => {
            dock.hide();
        });

        networkLayer.batchDraw();
    }

    updatePosition() {
        const y = getNetworkDivSize().height - this.json["y"];
        this.innerCircle.y(y);
        this.outerCircle.y(y);
        this.info.y(y);
        this.dockList.forEach(dock => {
            dock.y(y);
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

    update(stationJSON) {
        this.json = stationJSON;
    }
}

export function updateStationFromJSON(stationJSON) {
    let targetStations = appState.objects.filter(station => station.uuid.includes(stationJSON["uuid"]));
    targetStations.forEach(station => station.update(stationJSON));
}
