let networkDiv = document.getElementById('network-div');

let clearing = false;
let waitingSimLoopEnd = false;
let networkSize = 1000;
let objectScale;
let stage = new Konva.Stage({
    container: 'network-div',
    width: getNetworkDivSize().width,
    height: getNetworkDivSize().height
});
let networkLayer = new Konva.Layer();
let infoLayer = new Konva.Layer();

let scaleSlider = document.getElementById('scale-slider');
let startButton = document.getElementById('start-button');
let backwardButton = document.getElementById('backward-button');
let forwardButton = document.getElementById('forward-button');
let timerSpan = document.getElementById('timer-span');
let speedSpan = document.getElementById('speed-span');

let selectedObject = undefined;
let objects;

const defaultCapsuleWidth = 5;
const loopColor = 'rgb(156, 156, 156)';
const loopSelectedColor = 'rgb(255, 200, 20)';
const stationColor = 'rgb(40, 40, 200)';
const stationSelectedColor = 'rgb(255, 200, 20)';
const warehouseColor = 'rgb(40, 40, 40)';
const warehouseSelectedColor = 'rgb(255, 200, 20)';
const switchColor = 'rgb(200, 40, 40)';
const switchSelectedColor = 'rgb(255, 200, 20)';
const capsuleInnerEmptyColor = 'rgb(173, 72, 45)';
const capsuleOuterEmptyColor = 'rgb(255, 100, 63)';
const capsuleInnerAboardColor = 'rgb(96, 167, 27)';
const capsuleOuterAboardColor = 'rgb(128, 214, 30)';
const capsuleInnerSelectedColor = 'rgb(255, 200, 20)';
const capsuleOuterSelectedColor = 'rgb(255, 234, 87)';

function fetchTimeout(timeout, url, options) {
    const controller = new AbortController();
    const {signal} = controller;
    setTimeout(() => controller.abort(), timeout);
    return fetch(url, {...options, signal});
}

class Loop {
    constructor(loopJSON) {
        this.json = loopJSON;
        this.uuid = loopJSON['uuid'];
        this.id = loopJSON['id'];

        const x = loopJSON['x'];
        const y = getNetworkDivSize().height - loopJSON['y'];
        const semiWidth = ((defaultCapsuleWidth + 3) * objectScale) / 2;
        const strokeWidth = semiWidth / 2.5;

        this.innerCircle = new Konva.Circle({
            name: this.uuid,
            x: x,
            y: y,
            radius: loopJSON['radius'] - semiWidth,
            fill: 'white',
            stroke: 'black',
            strokeWidth: strokeWidth
        });

        this.outerCircle = new Konva.Circle({
            name: this.uuid,
            x: x,
            y: y,
            radius: loopJSON['radius'] + semiWidth,
            fill: loopColor,
            stroke: 'black',
            strokeWidth: strokeWidth
        });

        this.text = new Konva.Text({
            name: this.uuid,
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

        initBehaviors(this, this.innerCircle, this.outerCircle);

        networkLayer.add(this.outerCircle);
        networkLayer.add(this.innerCircle);
        networkLayer.add(this.text);

        objects.push(this);
    }

    select() {
        if (selectedObject !== undefined && selectedObject !== this) {
            selectedObject.unselect();
        }

        selectedObject = this;
        this.outerCircle.fill(loopSelectedColor);
        networkLayer.batchDraw();
    }

    unselect() {
        if (selectedObject === this) {
            selectedObject = undefined;
        }
        this.outerCircle.fill(loopColor);
        networkLayer.batchDraw();
    }

    updatePosition() {
        const y = getNetworkDivSize().height - this.json['y'];
        this.innerCircle.y(y);
        this.outerCircle.y(y);
        this.text.y(y);
    }

    updateScale(value) {
        const semiWidth = ((defaultCapsuleWidth + 3) * objectScale) / 2;
        const strokeWidth = semiWidth / 2.5;
        this.innerCircle.radius(this.json['radius'] - semiWidth);
        this.outerCircle.radius(this.json['radius'] + semiWidth);
        this.innerCircle.strokeWidth(strokeWidth);
        this.outerCircle.strokeWidth(strokeWidth);
        this.text.scaleX(value);
        this.text.scaleY(value);
    }
}

class Station {
    constructor(stationJSON, stationRadius = 12, stationWidth = 4, dockSize = 24) {
        this.json = stationJSON;
        this.uuid = stationJSON['uuid'];
        this.id = stationJSON['id'];
        this.capacity = stationJSON['capacity'];
        this.stationRadius = stationRadius;
        this.dockSize = dockSize;

        this.x = stationJSON['x'];
        const x = this.x;
        this.y = stationJSON['y'];
        const y = getNetworkDivSize().height - this.y;
        const semiWidth = Math.floor(stationWidth / 2);

        this.innerCircle = new Konva.Circle({
            name: this.uuid,
            x: x,
            y: y,
            radius: stationRadius - semiWidth,
            fill: 'white',
            stroke: 'black',
            strokeWidth: 0.3,
        });

        this.outerCircle = new Konva.Circle({
            name: this.uuid,
            x: x,
            y: y,
            radius: stationRadius + semiWidth,
            fill: stationColor,
            stroke: 'black',
            strokeWidth: 0.3,
        });

        this.dockList = [];
        for (let i = 0; i < this.capacity; i++) {
            let dockRect = new Konva.Rect({
                name: this.uuid,
                x: x + 10 * stationRadius + (6 * i + 2) * dockSize,
                y: y,
                width: dockSize,
                height: dockSize,
                fill: 'white',
                stroke: 'black',
                strokeWidth: 1,
            });
            dockRect.offsetX(dockRect.width() / 2);
            dockRect.offsetY(dockRect.height() / 2);
            this.dockList.push(dockRect);
        }

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

        initBehaviors(this, this.innerCircle, this.outerCircle, this.info);

        networkLayer.add(this.outerCircle);
        networkLayer.add(this.innerCircle);
        this.dockList.forEach(dock => {
            networkLayer.add(dock);
            dock.hide();
        });
        infoLayer.add(this.info);

        objects.push(this);
    }

    select() {
        if (selectedObject !== undefined && selectedObject !== this) {
            selectedObject.unselect();
        }

        selectedObject = this;
        this.outerCircle.fill(stationSelectedColor);

        this.dockList.forEach(dock => {
            dock.show();
        });

        networkLayer.batchDraw();
    }

    unselect() {
        if (selectedObject === this) {
            selectedObject = undefined;
        }
        this.outerCircle.fill(stationColor);

        this.dockList.forEach(dock => {
            dock.hide();
        });

        networkLayer.batchDraw();
    }

    updatePosition() {
        const y = getNetworkDivSize().height - this.y;
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
/*
class Star {
    constructor(warehouseJSON, starRadius = 12, starWidth = 4) {
        this.json = warehouseJSON;
        this.uuid = warehouseJSON['uuid'];
        this.id = warehouseJSON['id'];

        const x = warehouseJSON['x'];
        this.y = warehouseJSON['y'];
        const y = getNetworkDivSize().height - this.y;
        const semiWidth = Math.floor(warehouseWidth / 2);

        var star = new Konva.Star({
          x: x,
          y: y,
          numPoints: 5,
          innerRadius: 70,
          outerRadius: 70,
          fill: 'red',
          stroke: 'black',
          strokeWidth: 4
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
                text: 'Route coupée'],
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

        objects.push(this);
    }

    select() {
        if (selectedObject !== undefined && selectedObject !== this) {
            selectedObject.unselect();
        }

        selectedObject = this;
        this.outerRectangle.fill(warehouseSelectedColor);
        networkLayer.batchDraw();
    }

    unselect() {
        if (selectedObject === this) {
            selectedObject = undefined;
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
*/
class Warehouse {
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

        objects.push(this);
    }

    select() {
        if (selectedObject !== undefined && selectedObject !== this) {
            selectedObject.unselect();
        }

        selectedObject = this;
        this.outerRectangle.fill(warehouseSelectedColor);
        networkLayer.batchDraw();
    }

    unselect() {
        if (selectedObject === this) {
            selectedObject = undefined;
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

class Switch {
    constructor(switchJSON, switchRadius = 12, switchWidth = 4) {
        this.json = switchJSON;
        this.uuid = switchJSON['uuid'];
        this.id = switchJSON['id'];

        const xIn = switchJSON['xIn'];
        const yIn = getNetworkDivSize().height - switchJSON['yIn'];
        const xOut = switchJSON['xOut'];
        const yOut = getNetworkDivSize().height - switchJSON['yOut'];
        const semiWidth = Math.floor(switchWidth / 2);

        this.innerInCircle = new Konva.Circle({
            x: xIn,
            y: yIn,
            radius: switchRadius - semiWidth,
            fill: 'white',
            stroke: 'black',
            strokeWidth: 0.3,
        });

        this.outerInCircle = new Konva.Circle({
            name: this.uuid,
            x: xIn,
            y: yIn,
            radius: switchRadius + semiWidth,
            fill: switchColor,
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
            name: this.uuid,
            x: xOut,
            y: yOut,
            radius: switchRadius + semiWidth,
            fill: switchColor,
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

        initBehaviors(this, this.innerInCircle, this.outerInCircle, this.infoIn);
        initBehaviors(this, this.innerOutCircle, this.outerOutCircle, this.infoOut);

        networkLayer.add(this.arrow);
        networkLayer.add(this.link);
        networkLayer.add(this.outerInCircle);
        networkLayer.add(this.innerInCircle);
        networkLayer.add(this.outerOutCircle);
        networkLayer.add(this.innerOutCircle);
        infoLayer.add(this.infoIn);
        infoLayer.add(this.infoOut);

        objects.push(this);
    }

    select() {
        if (selectedObject !== undefined && selectedObject !== this) {
            selectedObject.unselect();
        }

        selectedObject = this;
        this.arrow.stroke(switchSelectedColor);
        this.arrow.fill(switchSelectedColor);
        this.outerInCircle.fill(switchSelectedColor);
        this.outerOutCircle.fill(switchSelectedColor);
        networkLayer.batchDraw();
    }

    unselect() {
        if (selectedObject === this) {
            selectedObject = undefined;
        }
        this.arrow.stroke('black');
        this.arrow.fill('black');
        this.outerInCircle.fill(switchColor);
        this.outerOutCircle.fill(switchColor);
        networkLayer.batchDraw();
    }

    updatePosition() {
        const height = getNetworkDivSize().height;
        const xIn = this.json['xIn'];
        const yIn = height - this.json['yIn'];
        const xOut = this.json['xOut'];
        const yOut = height - this.json['yOut'];

        this.innerInCircle.y(yIn);
        this.outerInCircle.y(yIn);
        this.innerOutCircle.y(yOut);
        this.outerOutCircle.y(yOut);
        this.infoIn.y(yIn);
        this.infoOut.y(yOut);
        this.link.points([xIn, yIn, xOut, yOut]);
        this.arrow.points([xIn, yIn, (xIn + xOut) / 2, (yIn + yOut) / 2]);
    }

    updateScale(value) {
        this.innerInCircle.scaleX(value);
        this.innerInCircle.scaleY(value);
        this.outerInCircle.scaleX(value);
        this.outerInCircle.scaleY(value);
        this.innerOutCircle.scaleX(value);
        this.innerOutCircle.scaleY(value);
        this.outerOutCircle.scaleX(value);
        this.outerOutCircle.scaleY(value);
        this.infoIn.scaleX(value);
        this.infoIn.scaleY(value);
        this.infoOut.scaleX(value);
        this.infoOut.scaleY(value);
        this.link.strokeWidth(2 * value);
        this.arrow.strokeWidth(2 * value);
        this.arrow.pointerWidth(10 * value);
        this.arrow.pointerLength(10 * value);
    }
}

class Capsule {
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

        objects.push(this);
    }

    select() {
        if (selectedObject !== undefined && selectedObject !== this) {
            selectedObject.unselect();
        }

        selectedObject = this;
        this.innerCircle.fill(capsuleInnerSelectedColor);
        this.outerCircle.fill(capsuleOuterSelectedColor);
        networkLayer.batchDraw();
    }

    unselect() {
        if (selectedObject === this) {
            selectedObject = undefined;
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
            let targetStations = objects.filter(station => station.uuid.includes(capsuleJSON['currentElementUuid']));
            targetStations.forEach(station => {
                this.innerCircle.x(x + 10 * station.stationRadius + (6 * capsuleJSON['stationIndex'] + 2) * station.dockSize);
                this.outerCircle.x(x + 10 * station.stationRadius + (6 * capsuleJSON['stationIndex'] + 2) * station.dockSize);
            });
        }

        this.updateColor();
    }

    updateColor() {
        if (selectedObject === this) {
            return;
        }

        if (this.isDocked) {
            if (selectedObject === undefined || this.currentElementUuid !== selectedObject.uuid) {
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

function handCursor() {
    document.body.style.cursor = 'pointer';
}

function moveCursor() {
    document.body.style.cursor = 'move';
}

function resetCursor() {
    document.body.style.cursor = 'auto';
}

function initBehaviors(object, innerShape, outerShape, info = undefined) {
    const hasInfo = info !== undefined;

    innerShape.on('mousedown', () => {
        object.select();
    });

    outerShape.on('mousedown', () => {
        object.select();
    });

    innerShape.on('mouseover', () => {
        handCursor();
        if (hasInfo) {
            info.show();
            infoLayer.batchDraw();
        }
    });

    outerShape.on('mouseover', () => {
        handCursor();
        if (hasInfo) {
            info.show();
            infoLayer.batchDraw();
        }
    });

    innerShape.on('mouseout', () => {
        moveCursor();
        if (hasInfo) {
            info.hide();
            infoLayer.batchDraw();
        }
    });

    outerShape.on('mouseout', () => {
        moveCursor();
        if (hasInfo) {
            info.hide();
            infoLayer.batchDraw();
        }
    });
}

async function initNetworkScene(networkName, isDefaultNetwork) {
    objects = [];

    let waitStart = new Date();
    while (waitingSimLoopEnd && (new Date() - waitStart) < 1000) {
        const offSignalJSON = await (await fetch('/loop-off-signal.json')).json();
        waitingSimLoopEnd = !offSignalJSON['loopOffSignal'];
    }

    startButton.classList.remove('not-shown');

    const networkJSON = await (await fetch(isDefaultNetwork ? '/load.json' : '/load.json/' + networkName)).json();
    networkSize = networkJSON['maxSize'];

    const listLoopJSON = await (await fetch('/loops.json')).json();
    for (const loopJSON of listLoopJSON) {
        new Loop(loopJSON);
    }

    const listStationSetDataJSON = await (await fetch('/stationsSetData.json')).json();
    for (const stationSetDataJSON of listStationSetDataJSON) {
        new Station(stationSetDataJSON);
    }

    const listWarehouseSetDataJSON = await (await fetch('/warehousesSetData.json')).json();
    for (const warehouseSetDataJSON of listWarehouseSetDataJSON) {
        new Warehouse(warehouseSetDataJSON);
    }

    const listSwitchSetDataJSON = await (await fetch('/switchesSetData.json')).json();
    for (const switchSetDataJSON of listSwitchSetDataJSON) {
        new Switch(switchSetDataJSON);
    }

    calibrateNetworkScene();

    networkLayer.batchDraw();
    infoLayer.batchDraw();
}

async function updateNetworkScene() {
    const listDataJSON = await (await fetchTimeout(100, '/updatedData.json')).json();

    if (!clearing) {
        for (const dataJSON of listDataJSON) {
            switch (dataJSON['jsonType']) {
                case 'time':
                    updateTimeFromJSON(dataJSON);
                    break;
                case 'station':
                    updateStationFromJSON(dataJSON);
                    break;
                case 'warehouse':
                    updateWarehouseFromJSON(dataJSON);
                    break;
                case 'switch':
                    updateSwitchFromJSON(dataJSON);
                    break;
                case 'capsule':
                    updateCapsuleFromJSON(dataJSON);
                    break;
            }
        }
    }

    networkLayer.batchDraw();
    infoLayer.batchDraw();
}

function updateTimeFromJSON(timeJSON) {
    timerSpan.innerHTML = "Day " + timeJSON['day'] + "<br><br>" + timeJSON['time'];
    speedSpan.innerHTML = timeJSON['speed'];

    if (timeJSON['decelerateJerky'] === 1) {
        if (!backwardButton.classList.contains("btn-warning")) {
            backwardButton.classList.remove("btn-light");
            backwardButton.classList.add("btn-warning");
            backwardButton.title = "Jerky Mode ! Simulation will be less accurate";
        }
    } else {
        if (!backwardButton.classList.contains("btn-light")) {
            backwardButton.classList.remove("btn-warning");
            backwardButton.classList.add("btn-light");
            backwardButton.removeAttribute("title");
        }
    }

    if (timeJSON['accelerateJerky'] === 1) {
        if (!forwardButton.classList.contains("btn-warning")) {
            forwardButton.classList.remove("btn-light");
            forwardButton.classList.add("btn-warning");
            forwardButton.title = "Jerky Mode ! Simulation will be less accurate";
        }
    } else {
        if (!forwardButton.classList.contains("btn-light")) {
            forwardButton.classList.remove("btn-warning");
            forwardButton.classList.add("btn-light");
            forwardButton.removeAttribute("title");
        }
    }
}

function updateStationFromJSON(stationJSON) {
    let targetStations = objects.filter(station => station.uuid.includes(stationJSON['uuid']));
    targetStations.forEach(station => station.update(stationJSON));
}

function updateWarehouseFromJSON(warehouseJSON) {
    let targetWarehouses = objects.filter(warehouse => warehouse.uuid.includes(warehouseJSON['uuid']));
    targetWarehouses.forEach(warehouse => warehouse.update(warehouseJSON));
}

function updateSwitchFromJSON(switchJSON) {

}

function updateCapsuleFromJSON(capsuleJSON) {
    let targetCapsules = objects.filter(capsule => capsule.uuid.includes(capsuleJSON['uuid']));

    if (targetCapsules.length <= 0) {
        new Capsule(capsuleJSON).updateScale(objectScale);
    } else {
        targetCapsules.forEach(capsule => capsule.update(capsuleJSON));
    }
}

function calibrateNetworkScene() {
    calibrateStageScale();
    objectScale = Math.min(networkSize / getNetworkDivSize().height, scaleSlider.max);
    scaleSlider.value = objectScale;
    scaleSlider.title = "Objects scale : " + scaleSlider.value;
    calibrateStagePosition();
    scaleObjects();
}

function getBarycenter() {
    let loopNumber = 0;
    let sumX = 0;
    let sumY = 0;

    objects.forEach(object => {
        if (object instanceof Loop) {
            loopNumber += 1;
            sumX += object.json['x'];
            sumY += getNetworkDivSize().height - object.json['y'];
        }
    });

    if (loopNumber === 0) {
        return {x: 0, y: 0};
    }

    return {x: sumX / loopNumber, y: sumY / loopNumber};
}

function calibrateStagePosition() {
    if (objectScale === 0) return;
    const barycenter = getBarycenter();
    const scale = networkSize / Math.min(getNetworkDivSize().width, getNetworkDivSize().height);
    const stagePos = {
        x: -barycenter.x / scale + getNetworkDivSize().width / 2,
        y: -barycenter.y / scale + getNetworkDivSize().height / 2
    };
    stage.position(stagePos);
}

function calibrateStageScale() {
    const stageScale = Math.min(getNetworkDivSize().width, getNetworkDivSize().height) / networkSize;
    stage.scale({x: stageScale, y: stageScale});
}

function scaleObjects() {
    objects.forEach(object => object.updateScale(objectScale));
}

function getNetworkDivSize() {
    return {
        width: Math.min(networkDiv.offsetWidth, window.innerWidth),
        height: Math.min(networkDiv.offsetHeight, window.innerHeight)
    }
}
