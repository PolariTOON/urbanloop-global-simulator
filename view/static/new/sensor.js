
const sensorColor = 'rgb(188,13,255)';
const sensorSelectedColor = 'rgb(255, 200, 20)';

export class Sensor {
    constructor(sensorJSON, sensorRadius = 12, sensorWidth = 4) {
        this.json = sensorJSON;
        this.uuid = sensorJSON['uuid'];
        this.id = sensorJSON['id'];
        this.sensorRadius = sensorRadius;
        this.x = sensorJSON['x'];
        const x = this.x;
        this.y = sensorJSON['y'];
        const y = getNetworkDivSize().height - this.y;
        const semiWidth = Math.floor(sensorWidth / 2);

        this.innerCircle = new Konva.Circle({
            name: this.uuid,
            x: x,
            y: y,
            radius: sensorRadius - semiWidth,
            fill: 'white',
            stroke: 'black',
            strokeWidth: 0.3,
        });

        this.outerCircle = new Konva.Circle({
            name: this.uuid,
            x: x,
            y: y,
            radius: sensorRadius + semiWidth,
            fill: sensorColor,
            stroke: 'black',
            strokeWidth: 0.3,
        });

        this.info = new Konva.Label({
            x: x,
            y: y,
            opacity: 0.75,
            visible: false,
            listening: false
        });

        this.info.add(
            new Konva.Tag({
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
            new Konva.Text({
                text: 'Sensor : ' + sensorJSON['name'],
                fontFamily: 'Calibri',
                fontSize: 18,
                padding: 5,
                fill: 'white'
            })
        );

        initBehaviors(this, this.innerCircle, this.outerCircle, this.info);

        networkLayer.add(this.outerCircle);
        networkLayer.add(this.innerCircle);
        infoLayer.add(this.info);

        appState.objects.push(this);
    }

    select() {
        if (appState.selectedObject !== undefined && appState.selectedObject !== this) {
            appState.selectedObject.unselect();
        }

        appState.selectedObject = this;
        this.outerCircle.fill(sensorSelectedColor);
        networkLayer.batchDraw();
    }

    unselect() {
        if (appState.selectedObject === this) {
            appState.selectedObject = undefined;
        }
        this.outerCircle.fill(sensorColor);
        networkLayer.batchDraw();
    }

    updatePosition() {
        const y = getNetworkDivSize().height - this.y;
        this.innerCircle.y(y);
        this.outerCircle.y(y);
        this.info.y(y);
    }

    updateScale(value) {
        this.innerCircle.scaleX(value);
        this.innerCircle.scaleY(value);
        this.outerCircle.scaleX(value);
        this.outerCircle.scaleY(value);
        this.info.scaleX(value);
        this.info.scaleY(value);
    }

    update(sensorJSON) {
        this.json = sensorJSON;
    }

}

function updateSensorFromJSON(sensorJSON) {
    let targetSensor = appState.objects.filter(sensor => sensor.uuid.includes(sensorJSON['uuid']));
    targetSensor.forEach(sensor => sensor.update(sensorJSON));
}