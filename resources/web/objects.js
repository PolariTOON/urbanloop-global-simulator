let networkDiv = document.getElementById('network-div');

let networkLayer;
let infoLayer;

let selectedObject = undefined;
let capsules;

const loopColor = 'rgb(156, 156, 156)';
const loopSelectedColor = 'rgb(255, 200, 20)';
const stationColor = 'rgb(40, 40, 200)';
const stationSelectedColor = 'rgb(255, 200, 20)';
const switchColor = 'rgb(200, 40, 40)';
const switchSelectedColor = 'rgb(255, 200, 20)';
const capsuleInnerEmptyColor = 'rgb(173, 72, 45)';
const capsuleOuterEmptyColor = 'rgb(255, 100, 63)';
const capsuleInnerAboardColor = 'rgb(96, 167, 27)';
const capsuleOuterAboardColor = 'rgb(128, 214, 30)';
const capsuleInnerSelectedColor = 'rgb(255, 200, 20)';
const capsuleOuterSelectedColor = 'rgb(255, 234, 87)';

class Loop {
    constructor(loopJSON, loopWidth = 6, strokeWidth = 2) {
        this.json = loopJSON;
        this.uuid = loopJSON['uuid'];
        this.id = loopJSON['id'];

        let x = loopJSON['x'];
        let y = networkDiv.offsetHeight - loopJSON['y'];
        let semiWidth = Math.floor(loopWidth / 2);

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
}

class Station {
    constructor(stationJSON, stationRadius = 12, stationWidth = 4) {
        this.json = stationJSON;
        this.uuid = stationJSON['uuid'];
        this.id = stationJSON['id'];

        let x = stationJSON['x'];
        let y = networkDiv.offsetHeight - stationJSON['y'];
        let semiWidth = Math.floor(stationWidth / 2);

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
        infoLayer.add(this.info);
    }

    select() {
        if (selectedObject !== undefined && selectedObject !== this) {
            selectedObject.unselect();
        }

        selectedObject = this;
        this.outerCircle.fill(stationSelectedColor);
        networkLayer.batchDraw();
    }

    unselect() {
        if (selectedObject === this) {
            selectedObject = undefined;
        }
        this.outerCircle.fill(stationColor);
        networkLayer.batchDraw();
    }
}

class Switch {
    constructor(switchJSON, switchRadius = 12, switchWidth = 4) {
        this.json = switchJSON;
        this.uuid = switchJSON['uuid'];
        this.id = switchJSON['id'];

        let xIn = switchJSON['xIn'];
        let yIn = networkDiv.offsetHeight - switchJSON['yIn'];
        let xOut = switchJSON['xOut'];
        let yOut = networkDiv.offsetHeight - switchJSON['yOut'];
        let semiWidth = Math.floor(switchWidth / 2);

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
}

class Capsule {
    constructor(capsuleJSON, capsuleWidth = 5) {
        this.json = capsuleJSON;
        this.uuid = capsuleJSON['uuid'];
        this.id = capsuleJSON['id'];
        this.travelerNumber = capsuleJSON['travelerNumber'];

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

        capsules.push(this);
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

function initBehaviors(object, innerCircle, outerCircle, info = undefined) {
    let hasInfo = info !== undefined;

    innerCircle.on('mousedown', () => {
        object.select();
    });

    outerCircle.on('mousedown', () => {
        object.select();
    });

    innerCircle.on('mouseover', () => {
        handCursor();
        if (hasInfo) {
            info.show();
            infoLayer.batchDraw();
        }
    });

    outerCircle.on('mouseover', () => {
        handCursor();
        if (hasInfo) {
            info.show();
            infoLayer.batchDraw();
        }
    });

    innerCircle.on('mouseout', () => {
        resetCursor();
        if (hasInfo) {
            info.hide();
            infoLayer.batchDraw();
        }
    });

    outerCircle.on('mouseout', () => {
        resetCursor();
        if (hasInfo) {
            info.hide();
            infoLayer.batchDraw();
        }
    });
}

function initNetworkScene() {
    $.ajaxSetup({async: false});

    $.get('/load');

    $.get('/loops.json', function (listLoopJSON) {
        listLoopJSON.forEach(function (loopJSON) {
            new Loop(loopJSON);
        });
    });

    $.get('/stationsSetData.json', function (listStationSetDataJSON) {
        listStationSetDataJSON.forEach(function (stationSetDataJSON) {
            new Station(stationSetDataJSON);
        });
    });

    $.get('/switchesSetData.json', function (listSwitchSetDataJSON) {
        listSwitchSetDataJSON.forEach(function (switchSetDataJSON) {
            new Switch(switchSetDataJSON);
        });
    });

    capsules = [];

    $.ajaxSetup({async: true});

    networkLayer.batchDraw();
    infoLayer.batchDraw();
}

function updateNetworkScene() {
    /*$.get('/time.json', function (timeJSON) {
        document.getElementById('time-span').innerHTML = timeJSON['time']
    });*/

    $.get('/capsules.json', function (listCapsuleJSON) {
        listCapsuleJSON.forEach(function (capsuleJSON) {
            let targetCapsules = capsules.filter(capsule => capsule.uuid.includes(capsuleJSON['uuid']));

            if (targetCapsules.length <= 0) {
                new Capsule(capsuleJSON);
            } else {
                targetCapsules.forEach(capsule => capsule.update(capsuleJSON));
            }

        });
    });

    networkLayer.batchDraw();
    infoLayer.batchDraw();
}

