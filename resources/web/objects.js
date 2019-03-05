let networkDiv = document.getElementById('network-div');

let selectedObject = undefined;
let capsules;

const capsuleInnerEmptyColor = 'rgb(173, 72, 45)';
const capsuleOuterEmptyColor = 'rgb(255, 100, 63)';
const capsuleInnerAboardColor = 'rgb(96, 167, 27)';
const capsuleOuterAboardColor = 'rgb(128, 214, 30)';
const capsuleInnerSelectedColor = 'rgb(255, 200, 20)';
const capsuleOuterSelectedColor = 'rgb(255, 234, 87)';

class Loop {
    constructor(loopJSON, networkLayer, loopWidth = 4, strokeWidth = 2) {
        let x = loopJSON['x'];
        let y = networkDiv.offsetHeight - loopJSON['y'];
        let semiWidth = Math.floor(loopWidth / 2);

        this.json = loopJSON;
        this.networkLayer = networkLayer;
        this.id = 'loop:' + loopJSON['id'];
        this.color = 'rgb(156, 156, 156)';
        this.selectedColor = 'rgb(255, 200, 20)';

        this.background = new Konva.Circle({
            x: x,
            y: y,
            radius: loopJSON['radius'],
            fill: 'white'
        });

        this.loop = new Konva.Arc({
            name: this.id,
            x: x,
            y: y,
            innerRadius: loopJSON['radius'] - semiWidth,
            outerRadius: loopJSON['radius'] + semiWidth,
            fill: this.color,
            angle: 360
        });

        this.stroke = new Konva.Arc({
            name: this.id,
            x: x,
            y: y,
            innerRadius: loopJSON['radius'] - semiWidth - Math.floor(strokeWidth / 2),
            outerRadius: loopJSON['radius'] + semiWidth + Math.floor(strokeWidth / 2),
            stroke: 'black',
            strokeWidth: strokeWidth,
            angle: 360
        });

        this.text = new Konva.Text({
            x: x,
            y: y,
            text: loopJSON['name'],
            fontFamily: "Georgia, serif",
            fontSize: 20,
            fontVariant: "small-caps",
            fill: 'black'
        });
        this.text.offsetX(this.text.width() / 2);
        this.text.offsetY(this.text.height() / 2);

        this.loop.on('mousedown', () => {
            this.select();
        });

        this.stroke.on('mousedown', () => {
            this.select();
        });

        this.loop.on('mouseover', () => {
            handCursor();
        });

        this.stroke.on('mouseover', () => {
            handCursor();
        });

        this.loop.on('mouseout', () => {
            resetCursor();
        });

        this.stroke.on('mouseout', () => {
            resetCursor();
        });

        this.networkLayer.add(this.background);
        this.networkLayer.add(this.text);
        this.networkLayer.add(this.stroke);
        this.networkLayer.add(this.loop);
    }

    select() {
        if (selectedObject !== undefined && selectedObject !== this) {
            selectedObject.unselect();
        }

        selectedObject = this;
        this.loop.fill(this.selectedColor);
        this.networkLayer.batchDraw();
    }

    unselect() {
        if (selectedObject === this) {
            selectedObject = undefined;
        }
        this.loop.fill(this.color);
        this.networkLayer.batchDraw();
    }
}

class Station {
    constructor(stationJSON, networkLayer, infoLayer, stationRadius = 12, stationWidth = 4) {
        let x = stationJSON['x'];
        let y = networkDiv.offsetHeight - stationJSON['y'];
        let semiWidth = Math.floor(stationWidth / 2);

        this.json = stationJSON;
        this.networkLayer = networkLayer;
        this.infoLayer = infoLayer;
        this.id = 'station:' + stationJSON['id'];
        this.color = 'rgb(40, 40, 200)';
        this.selectedColor = 'rgb(255, 200, 20)';

        this.innerCircle = new Konva.Circle({
            x: x,
            y: y,
            radius: stationRadius - semiWidth,
            fill: 'white',
            stroke: 'black',
            strokeWidth: 0.3,
        });

        this.outerCircle = new Konva.Circle({
            name: this.id,
            x: x,
            y: y,
            radius: stationRadius + semiWidth,
            fill: this.color,
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
                text: 'Station : ' + stationJSON['name'] + ' | Capacity : ' + stationJSON['capacity'],
                fontFamily: 'Calibri',
                fontSize: 18,
                padding: 5,
                fill: 'white'
            })
        );

        this.outerCircle.on('mousedown', () => {
            this.select();
        });

        this.outerCircle.on('mouseover', () => {
            handCursor();
            this.info.show();
            this.infoLayer.batchDraw();
        });

        this.outerCircle.on('mouseout', () => {
            resetCursor();
            this.info.hide();
            this.infoLayer.batchDraw();
        });

        this.networkLayer.add(this.outerCircle);
        this.networkLayer.add(this.innerCircle);
        this.infoLayer.add(this.info);
    }

    select() {
        if (selectedObject !== undefined && selectedObject !== this) {
            selectedObject.unselect();
        }

        selectedObject = this;
        this.outerCircle.fill(this.selectedColor);
        this.networkLayer.batchDraw();
    }

    unselect() {
        if (selectedObject === this) {
            selectedObject = undefined;
        }
        this.outerCircle.fill(this.color);
        this.networkLayer.batchDraw();
    }
}



class Station {
    constructor(warehouseJSON, networkLayer, infoLayer, warehouseRadius = 20, warehouseWidth = 20) {
        let x = warehouseJSON['x'];
        let y = networkDiv.offsetHeight - warehouseJSON['y'];
        let semiWidth = Math.floor(warehouseWidth / 2);

        this.json = warehouseJSON;
        this.networkLayer = networkLayer;
        this.infoLayer = infoLayer;
        this.id = 'warehouse:' + warehouseJSON['id'];
        this.color = 'rgb(40, 40, 40)';
        this.selectedColor = 'rgb(255, 200, 20)';

        this.innerCircle = new Konva.Circle({
            x: x,
            y: y,
            radius: warehouseRadius - semiWidth,
            fill: 'white',
            stroke: 'black',
            strokeWidth: 0.3,
        });

        this.outerCircle = new Konva.Circle({
            name: this.id,
            x: x,
            y: y,
            radius: warehouseRadius + semiWidth,
            fill: this.color,
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
                text: 'Warehouse : ' + warehouseJSON['name'] + ' | Capacity : ' + warehouseJSON['capacity'],
                fontFamily: 'Calibri',
                fontSize: 18,
                padding: 5,
                fill: 'white'
            })
        );

        this.outerCircle.on('mousedown', () => {
            this.select();
        });

        this.outerCircle.on('mouseover', () => {
            handCursor();
            this.info.show();
            this.infoLayer.batchDraw();
        });

        this.outerCircle.on('mouseout', () => {
            resetCursor();
            this.info.hide();
            this.infoLayer.batchDraw();
        });

        this.networkLayer.add(this.outerCircle);
        this.networkLayer.add(this.innerCircle);
        this.infoLayer.add(this.info);
    }

    select() {
        if (selectedObject !== undefined && selectedObject !== this) {
            selectedObject.unselect();
        }

        selectedObject = this;
        this.outerCircle.fill(this.selectedColor);
        this.networkLayer.batchDraw();
    }

    unselect() {
        if (selectedObject === this) {
            selectedObject = undefined;
        }
        this.outerCircle.fill(this.color);
        this.networkLayer.batchDraw();
    }
}


class Switch {
    constructor(switchJSON, networkLayer, infoLayer, switchRadius = 12, switchWidth = 4) {
        let xIn = switchJSON['xIn'];
        let yIn = networkDiv.offsetHeight - switchJSON['yIn'];
        let xOut = switchJSON['xOut'];
        let yOut = networkDiv.offsetHeight - switchJSON['yOut'];
        let semiWidth = Math.floor(switchWidth / 2);

        this.json = switchJSON;
        this.networkLayer = networkLayer;
        this.infoLayer = infoLayer;
        this.id = 'switch:' + switchJSON['id'];
        this.color = 'rgb(200, 40, 40)';
        this.selectedColor = 'rgb(255, 200, 20)';

        this.innerInCircle = new Konva.Circle({
            x: xIn,
            y: yIn,
            radius: switchRadius - semiWidth,
            fill: 'white',
            stroke: 'black',
            strokeWidth: 0.3,
        });

        this.outerInCircle = new Konva.Circle({
            name: this.id,
            x: xIn,
            y: yIn,
            radius: switchRadius + semiWidth,
            fill: this.color,
            stroke: 'black',
            strokeWidth: 0.3,
        });

        this.innerOutCircle = new Konva.Circle({
            x: xOut,
            y: yOut,
            radius: switchRadius - semiWidth,
            fill: 'white',
            stroke: 'black',
            strokeWidth: 0.3,
        });

        this.outerOutCircle = new Konva.Circle({
            name: this.id,
            x: xOut,
            y: yOut,
            radius: switchRadius + semiWidth,
            fill: this.color,
            stroke: 'black',
            strokeWidth: 0.3,
        });

        this.link = new Konva.Line({
            points: [xIn, yIn, xOut, yOut],
            stroke: 'black',
            strokeWidth: 2,
        });

        this.arrow = new Konva.Arrow({
            points: [xIn, yIn, (xIn + xOut) / 2, (yIn + yOut) / 2],
            pointerLength: 10,
            pointerWidth: 10,
            fill: 'black',
            stroke: 'black',
            strokeWidth: 2
        });

        this.infoIn = new Konva.Label({
            x: xIn,
            y: yIn,
            opacity: 0.75,
            visible: false,
            listening: false
        });

        this.infoOut = new Konva.Label({
            x: xOut,
            y: yOut,
            opacity: 0.75,
            visible: false,
            listening: false
        });

        this.infoIn.add(new Konva.Tag({
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

        this.infoOut.add(new Konva.Tag({
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

        this.infoIn.add(
            new Konva.Text({
                text: switchJSON['nameIn'],
                fontFamily: 'Calibri',
                fontSize: 18,
                padding: 5,
                fill: 'white'
            })
        );

        this.infoOut.add(
            new Konva.Text({
                text: switchJSON['nameOut'],
                fontFamily: 'Calibri',
                fontSize: 18,
                padding: 5,
                fill: 'white'
            })
        );

        this.outerInCircle.on('mousedown', () => {
            this.select();
        });

        this.outerOutCircle.on('mousedown', () => {
            this.select();
        });

        this.outerInCircle.on('mouseover', () => {
            handCursor();
            this.infoIn.show();
            this.infoLayer.batchDraw();
        });

        this.outerOutCircle.on('mouseover', () => {
            handCursor();
            this.infoOut.show();
            this.infoLayer.batchDraw();
        });

        this.outerInCircle.on('mouseout', () => {
            resetCursor();
            this.infoIn.hide();
            this.infoLayer.batchDraw();
        });

        this.outerOutCircle.on('mouseout', () => {
            resetCursor();
            this.infoOut.hide();
            this.infoLayer.batchDraw();
        });

        this.networkLayer.add(this.arrow);
        this.networkLayer.add(this.link);
        this.networkLayer.add(this.outerInCircle);
        this.networkLayer.add(this.innerInCircle);
        this.networkLayer.add(this.outerOutCircle);
        this.networkLayer.add(this.innerOutCircle);
        this.infoLayer.add(this.infoIn);
        this.infoLayer.add(this.infoOut);
    }

    select() {
        if (selectedObject !== undefined && selectedObject !== this) {
            selectedObject.unselect();
        }

        selectedObject = this;
        this.arrow.stroke(this.selectedColor);
        this.arrow.fill(this.selectedColor);
        this.outerInCircle.fill(this.selectedColor);
        this.outerOutCircle.fill(this.selectedColor);
        this.networkLayer.batchDraw();
    }

    unselect() {
        if (selectedObject === this) {
            selectedObject = undefined;
        }
        this.arrow.stroke('black');
        this.arrow.fill('black');
        this.outerInCircle.fill(this.color);
        this.outerOutCircle.fill(this.color);
        this.networkLayer.batchDraw();
    }
}

class Capsule {
    constructor(capsuleJSON, networkLayer, infoLayer, capsuleWidth = 5) {
        this.networkLayer = networkLayer;
        this.infoLayer = infoLayer;

        this.json = capsuleJSON;
        this.id = 'capsule:' + capsuleJSON['id'];
        this.travelerNumber = capsuleJSON['travelerNumber'];

        this.innerCircle = new Konva.Circle({
            name: this.id + ':inner',
            radius: capsuleWidth - Math.sqrt(capsuleWidth),
        });

        this.outerCircle = new Konva.Circle({
            name: this.id + ':outer',
            radius: capsuleWidth,
        });

        this.outerCircle.on('mousedown', () => {
            this.select();
        });
        this.innerCircle.on('mousedown', () => {
            this.select();
        });

        this.networkLayer.add(this.outerCircle);
        this.networkLayer.add(this.innerCircle);
        this.update(capsuleJSON);

        capsules.push(this);
    }

    select() {
        if (selectedObject !== undefined && selectedObject !== this) {
            selectedObject.unselect();
        }

        selectedObject = this;
        this.innerCircle.fill(capsuleInnerSelectedColor);
        this.outerCircle.fill(capsuleOuterSelectedColor);
        this.networkLayer.batchDraw();
    }

    unselect() {
        if (selectedObject === this) {
            selectedObject = undefined;
        }

        this.updateColor();
        this.networkLayer.batchDraw();
    }

    update(capsuleJSON) {
        let x = capsuleJSON['x'];
        let y = networkDiv.offsetHeight - capsuleJSON['y'];
        this.innerCircle.x(x);
        this.innerCircle.y(y);
        this.outerCircle.x(x);
        this.outerCircle.y(y);
        this.travelerNumber = capsuleJSON['travelerNumber'];

        this.updateColor();
    }

    updateColor() {
        if (selectedObject === this) {
            return;
        }

        if (this.isAboard()) {
            this.innerCircle.fill(capsuleInnerAboardColor);
            this.outerCircle.fill(capsuleOuterAboardColor);
        } else {
            this.innerCircle.fill(capsuleInnerEmptyColor);
            this.outerCircle.fill(capsuleOuterEmptyColor);
        }
    }

    isAboard() {
        return this.travelerNumber > 0;
    }
}

function handCursor() {
    document.body.style.cursor = 'pointer';
}

function resetCursor() {
    document.body.style.cursor = 'auto';
}

function initNetworkScene(networkLayer, infoLayer) {
    $.ajaxSetup({async: false});

    $.get('/load');

    $.get('/loops.json', function (listLoopJSON) {
        listLoopJSON.forEach(function (loopJSON) {
            new Loop(loopJSON, networkLayer);
        });
    });

    $.get('/stationsSetData.json', function (listStationSetDataJSON) {
        listStationSetDataJSON.forEach(function (stationSetDataJSON) {
            new Station(stationSetDataJSON, networkLayer, infoLayer);
        });
    });

    $.get('/warehousesSetData.json', function(listWarehouseSetDataJSON) {
        listWarehouseSetDataJSON.forEach(function (warehouseSetDataJSON){
            new Warehouse(warehouseSetDataJSON, networkLayer, infoLayer);
        });
    });
    $.get('/switchesSetData.json', function (listSwitchSetDataJSON) {
        listSwitchSetDataJSON.forEach(function (switchSetDataJSON) {
            new Switch(switchSetDataJSON, networkLayer, infoLayer);
        });
    });

    capsules = [];

    $.ajaxSetup({async: true});

    networkLayer.batchDraw();
    infoLayer.batchDraw();
}

function updateNetworkScene(networkLayer, infoLayer) {
    $.get('/time.json', function (timeJSON) {
        document.getElementById('time-span').innerHTML = timeJSON['time']
    });

    $.get('/capsules.json', function (listCapsuleJSON) {
        listCapsuleJSON.forEach(function (capsuleJSON) {
            let targetCapsules = capsules.filter(capsule => capsule.id.includes(capsuleJSON['id']));

            if (targetCapsules.length <= 0) {
                new Capsule(capsuleJSON, networkLayer, infoLayer);
            } else {
                targetCapsules.forEach(capsule => capsule.update(capsuleJSON));
            }

        });
    });

    networkLayer.batchDraw();
    infoLayer.batchDraw();
}

