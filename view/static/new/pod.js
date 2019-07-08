export const defaultCapsuleWidth = 5;
const capsuleInnerEmptyColor = 'rgb(173, 72, 45)';
const capsuleOuterEmptyColor = 'rgb(255, 100, 63)';
const capsuleInnerAboardColor = 'rgb(96, 167, 27)';
const capsuleOuterAboardColor = 'rgb(128, 214, 30)';
const capsuleInnerSelectedColor = 'rgb(255, 200, 20)';
const capsuleOuterSelectedColor = 'rgb(255, 234, 87)';

export class Pod {
    constructor(capsuleJSON, capsuleWidth = defaultCapsuleWidth) {
        this.json = capsuleJSON;
        this.uuid = capsuleJSON['uuid'];
        this.id = capsuleJSON['id'];
        this.travelerNumber = capsuleJSON['travelerNumber'];
        this.isDocked = true;

        this.innerCircle = new Konva.Circle({
            name: this.uuid,
            radius: capsuleWidth - Math.sqrt(capsuleWidth),
        });

        this.outerCircle = new Konva.Circle({
            name: this.uuid,
            radius: capsuleWidth,
        });

        initBehaviors(this, this.innerCircle, this.outerCircle);

        networkLayer.add(this.outerCircle);
        networkLayer.add(this.innerCircle);
        this.update(capsuleJSON);

        appState.objects.push(this);
    }

    select() {
        if (appState.selectedObject !== undefined && appState.selectedObject !== this) {
            appState.selectedObject.unselect();
        }

        appState.selectedObject = this;
        this.innerCircle.fill(capsuleInnerSelectedColor);
        this.outerCircle.fill(capsuleOuterSelectedColor);
        networkLayer.batchDraw();
    }

    unselect() {
        if (appState.selectedObject === this) {
            appState.selectedObject = undefined;
        }

        this.updateColor();
        networkLayer.batchDraw();
    }

    update(capsuleJSON) {
        const x = capsuleJSON['x'];
        const y = getNetworkDivSize().height - capsuleJSON['y'];
        this.innerCircle.x(x);
        this.innerCircle.y(y);
        this.outerCircle.x(x);
        this.outerCircle.y(y);
        this.isDocked = !capsuleJSON['moving'];
        this.travelerNumber = capsuleJSON['travelerNumber'];
        this.json = capsuleJSON;
        this.currentElementUuid = capsuleJSON['currentElementUuid'];

        if (this.isDocked) {
            if (capsuleJSON['stationIndex'] === -1) { // THIS IS HOTFIX FOR GHOST CAPS
                this.innerCircle.hide();
                this.outerCircle.hide();
                return;
            }
            let targetStations = appState.objects.filter(station => station.uuid.includes(capsuleJSON['currentElementUuid']));
            targetStations.forEach(station => {
                this.innerCircle.x(x + 10 * station.stationRadius + (6 * capsuleJSON['stationIndex'] + 2) * station.dockSize);
                this.outerCircle.x(x + 10 * station.stationRadius + (6 * capsuleJSON['stationIndex'] + 2) * station.dockSize);
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
            this.innerCircle.fill(capsuleInnerAboardColor);
            this.outerCircle.fill(capsuleOuterAboardColor);
        } else {
            this.innerCircle.fill(capsuleInnerEmptyColor);
            this.outerCircle.fill(capsuleOuterEmptyColor);
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

function updatePodFromJSON(capsuleJSON) {
    let targetCapsules = appState.objects.filter(capsule => capsule.uuid.includes(capsuleJSON['uuid']));

    if (targetCapsules.length <= 0) {
        new Capsule(capsuleJSON).updateScale(appState.objectScale);
    } else {
        targetCapsules.forEach(capsule => capsule.update(capsuleJSON));
    }
}