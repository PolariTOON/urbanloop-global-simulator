import {appState, getNetworkDivSize, initBehaviors} from "./network.js";

export const defaultPodWidth = 5;
const podInnerEmptyColor = 'rgb(173, 72, 45)';
const podOuterEmptyColor = 'rgb(255, 100, 63)';
const podInnerAboardColor = 'rgb(96, 167, 27)';
const podOuterAboardColor = 'rgb(128, 214, 30)';
const podInnerSelectedColor = 'rgb(255, 200, 20)';
const podOuterSelectedColor = 'rgb(255, 234, 87)';

export class Pod {
    constructor(podJSON, podWidth = defaultPodWidth) {
        this.json = podJSON;
        this.uuid = podJSON['uuid'];
        this.id = podJSON['id'];
        this.travelerNumber = podJSON['travelerNumber'];
        this.isDocked = true;

        this.innerCircle = new Konva.Circle({
            name: this.uuid,
            radius: podWidth - Math.sqrt(podWidth),
        });

        this.outerCircle = new Konva.Circle({
            name: this.uuid,
            radius: podWidth,
        });

        initBehaviors(this, this.innerCircle, this.outerCircle);

        networkLayer.add(this.outerCircle);
        networkLayer.add(this.innerCircle);
        this.update(podJSON);

        appState.objects.push(this);
    }

    select() {
        if (appState.selectedObject !== undefined && appState.selectedObject !== this) {
            appState.selectedObject.unselect();
        }

        appState.selectedObject = this;
        this.innerCircle.fill(podInnerSelectedColor);
        this.outerCircle.fill(podOuterSelectedColor);
        networkLayer.batchDraw();
    }

    unselect() {
        if (appState.selectedObject === this) {
            appState.selectedObject = undefined;
        }

        this.updateColor();
        networkLayer.batchDraw();
    }

    update(podJSON) {
        const x = podJSON['x'];
        const y = getNetworkDivSize().height - podJSON['y'];
        this.innerCircle.x(x);
        this.innerCircle.y(y);
        this.outerCircle.x(x);
        this.outerCircle.y(y);
        this.isDocked = !podJSON['moving'];
        this.travelerNumber = podJSON['travelerNumber'];
        this.json = podJSON;
        this.currentElementUuid = podJSON['currentElementUuid'];

        if (this.isDocked) {
            if (podJSON['stationIndex'] === -1) { // THIS IS HOTFIX FOR GHOST CAPS
                this.innerCircle.hide();
                this.outerCircle.hide();
                return;
            }
            let targetStations = appState.objects.filter(station => station.uuid.includes(podJSON['currentElementUuid']));
            targetStations.forEach(station => {
                this.innerCircle.x(x + 10 * station.stationRadius + (6 * podJSON['stationIndex'] + 2) * station.dockSize);
                this.outerCircle.x(x + 10 * station.stationRadius + (6 * podJSON['stationIndex'] + 2) * station.dockSize);
            });
        }

        this.updateColor();
    }

    updateColor() {
        if (appState.selectedObject === this) {
            return;
        }

        if (this.isDocked) {
            if (appState.selectedObject === undefined || this.currentElementUuid !== appState.selectedObject.uuid) {
                this.innerCircle.hide();
                this.outerCircle.hide();
            } else {
                this.innerCircle.show();
                this.outerCircle.show();
            }
        } else {
            this.innerCircle.show();
            this.outerCircle.show();
        }

        if (this.isAboard()) {
            this.innerCircle.fill(podInnerAboardColor);
            this.outerCircle.fill(podOuterAboardColor);
        } else {
            this.innerCircle.fill(podInnerEmptyColor);
            this.outerCircle.fill(podOuterEmptyColor);
        }
    }

    updateScale(value) {
        this.innerCircle.scaleX(value);
        this.innerCircle.scaleY(value);
        this.outerCircle.scaleX(value);
        this.outerCircle.scaleY(value);
    }

    isAboard() {
        return this.travelerNumber > 0;
    }
}

export function updatePodFromJSON(podJSON) {
    let targetPods = appState.objects.filter(pod => pod.uuid.includes(podJSON['uuid']));

    if (targetPods.length <= 0) {
        new Pod(podJSON).updateScale(appState.objectScale);
    } else {
        targetPods.forEach(pod => pod.update(podJSON));
    }
}