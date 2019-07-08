const shedColor = 'rgb(40, 40, 40)';
const shedSelectedColor = 'rgb(255, 200, 20)';

export class Shed {
    constructor(warehouseJSON, warehouseRadius = 12, warehouseWidth = 4) {
        this.json = warehouseJSON;
        this.uuid = warehouseJSON['uuid'];
        this.id = warehouseJSON['id'];

        const x = warehouseJSON['x'];
        this.y = warehouseJSON['y'];
        const y = getNetworkDivSize().height - this.y;
        const semiWidth = Math.floor(warehouseWidth / 2);

        this.innerRectangle = new Konva.Rect({
            name: this.uuid,
            x: x,
            y: y,
            width: 2 * (warehouseRadius - semiWidth),
            height: 2 * (warehouseRadius - semiWidth),
            fill: 'white',
            stroke: 'black',
            strokeWidth: 0.3,
        });
        this.innerRectangle.offsetX(this.innerRectangle.width() / 2);
        this.innerRectangle.offsetY(this.innerRectangle.height() / 2);

        this.outerRectangle = new Konva.Rect({
            name: this.uuid,
            x: x,
            y: y,
            width: 2 * (warehouseRadius + semiWidth),
            height: 2 * (warehouseRadius + semiWidth),
            fill: warehouseColor,
            stroke: 'black',
            strokeWidth: 0.3,
        });
        this.outerRectangle.offsetX(this.outerRectangle.width() / 2);
        this.outerRectangle.offsetY(this.outerRectangle.height() / 2);

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
                text: 'Warehouse : ' + warehouseJSON['name'] + ' | Capacity : ' + warehouseJSON['capacity'],
                fontFamily: 'Calibri',
                fontSize: 18,
                padding: 5,
                fill: 'white'
            })
        );

        initBehaviors(this, this.innerRectangle, this.outerRectangle, this.info);

        networkLayer.add(this.outerRectangle);
        networkLayer.add(this.innerRectangle);
        infoLayer.add(this.info);

        appState.objects.push(this);
    }

    select() {
        if (appState.selectedObject !== undefined && appState.selectedObject !== this) {
            appState.selectedObject.unselect();
        }

        appState.selectedObject = this;
        this.outerRectangle.fill(warehouseSelectedColor);
        networkLayer.batchDraw();
    }

    unselect() {
        if (appState.selectedObject === this) {
            appState.selectedObject = undefined;
        }
        this.outerRectangle.fill(warehouseColor);
        networkLayer.batchDraw();
    }

    updatePosition() {
        const y = getNetworkDivSize().height - this.y;
        this.innerRectangle.y(y);
        this.outerRectangle.y(y);
        this.info.y(y);
    }

    updateScale(value) {
        this.innerRectangle.scaleX(value);
        this.innerRectangle.scaleY(value);
        this.outerRectangle.scaleX(value);
        this.outerRectangle.scaleY(value);
        this.info.scaleX(value);
        this.info.scaleY(value);
    }

    update(warehouseJSON) {
        this.json = warehouseJSON;
    }
}

function updateShedFromJSON(warehouseJSON) {
    let targetWarehouses = appState.objects.filter(warehouse => warehouse.uuid.includes(warehouseJSON['uuid']));
    targetWarehouses.forEach(warehouse => warehouse.update(warehouseJSON));
}