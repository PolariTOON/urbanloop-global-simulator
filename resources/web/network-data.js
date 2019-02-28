let loops = [];
let stations = [];
let switches = [];
let capsules = [];

//TODO RENAME ALL IN DATA
class Loop {
    constructor(loopJSON) {
        this.id = loopJSON['id'];
        this.name = loopJSON['name'];
        this.radius = loopJSON['radius'];
        this.x = loopJSON['x'];
        this.y = loopJSON['y'];
        this.object = new LoopObject(this);
    }
}

class Station {
    constructor(stationSetData) {
        this.id = stationSetData.id;
        this.stationSetData = stationSetData;
        this.stationVarData = null;
        this.object = new StationObject(this.stationSetData, this.stationVarData)
    }

    update(stationVarDataJSON) {
        this.stationVarData = new StationVarData(stationVarDataJSON);
    }
}

class StationSetData {
    constructor(stationSetDataJSON) {
        this.id = stationSetDataJSON['id'];
        this.name = stationSetDataJSON['name'];
        this.loop = stationSetDataJSON['loop'];
        this.angle = stationSetDataJSON['angle'];
        this.capacity = stationSetDataJSON['capacity'];
    }
}

class StationVarData {
    constructor(stationVarDataJSON) {
        this.travelerNumber = stationVarDataJSON['travelerNumber'];
    }
}

class Switch {
    constructor(switchSetData) {
        this.id = switchSetData.id;
        this.switchSetData = switchSetData;
        this.switchVarData = null;
        this.object = new SwitchObject(this.switchSetData, this.switchVarData)
    }

    update(switchVarDataJSON) {
        this.switchVarData = new SwitchVarData(switchVarDataJSON);
    }
}

class SwitchSetData {
    constructor(switchSetDataJSON) {
        this.id = switchSetDataJSON['id'];
        this.loopIn = switchSetDataJSON['loopIn'];
        this.loopOut = switchSetDataJSON['loopOut'];
        this.angleLoopIn = switchSetDataJSON['angleLoopIn'];
        this.angleLoopOut = switchSetDataJSON['angleLoopOut'];
    }
}

class SwitchVarData {
    constructor(switchSetDataJSON) {
        this.defect = switchSetDataJSON['defect'];
    }
}

class Capsule {
    constructor(capsuleJSON) {
        this.update(capsuleJSON);
        this.object = new CapsuleObject(this);
    }

    isAboard() {
        return this.travelerNumber > 0;
    }

    update(capsuleJSON) {
        this.loopId = capsuleJSON['loopId'];
        this.currentElementId = capsuleJSON['currentElementId'];
        this.nextElementId = capsuleJSON['nextElementId'];
        this.segmentPercentage = capsuleJSON['segmentPercentage'];
        this.travelerNumber = capsuleJSON['travelerNumber'];
    }
}

function initData() {
    $.get('/load');

    $.get('/loops.json', function (listLoopJSON) {
        listLoopJSON.forEach(function (loopJSON) {
            loops.push(new Loop(loopJSON));
        });
    });

    $.get('/stationsSetData.json', function (listStationSetDataJSON) {
        listStationSetDataJSON.forEach(function (stationSetDataJSON) {
            stations.push(new Station(new StationSetData(stationSetDataJSON)));
        });
    });

    $.get('/switchesSetData.json', function (listSwitchSetDataJSON) {
        listSwitchSetDataJSON.forEach(function (switchSetDataJSON) {
            switches.push(new Switch(new SwitchSetData(switchSetDataJSON)));
        });
    });
}

function updateData() {
    /*$.get('/stationsVarData.json', function (listStationVarDataJSON) {
        listStationVarDataJSON.forEach(function (stationVarDataJSON) {
            getStationById(stationVarDataJSON['id']).update(stationVarDataJSON);
        });
    });

    $.get('/switchesVarData.json', function (listSwitchVarDataJSON) {
        listSwitchVarDataJSON.forEach(function (switchVarDataJSON) {
            getSwitchById(switchVarDataJSON['id']).update(switchVarDataJSON);
        });
    });*/

    $.get('/capsules.json', function (listCapsuleJSON) {
        console.log(capsules.length);
        listCapsuleJSON.forEach(function (capsuleJSON) {
            let aCapsule = getCapsuleById(capsuleJSON['id']);

            if (aCapsule === undefined) {
                capsules.push(new Capsule(capsuleJSON));
            } else {
                aCapsule.update();
            }
        });
    });
}

function getLoopById(loopId) {  // TODO change name by id
    for (let index in loops) {
        if (loops[index].name === loopId) {
            return loops[index];
        }
    }
    return undefined;
}

function getStationById(stationId) {
    for (let index in stations) {
        if (stations[index].id === stationId) {
            return stations[index];
        }
    }
    return undefined;
}

function getSwitchById(switchId) {
    for (let index in switches) {
        if (switches[index].id === switchId) {
            return switches[index];
        }
    }
    return undefined;
}

function getElementById(elementId) {
    let element = getStationById(elementId);
    return element === undefined ? getSwitchById(elementId) : element;
}

function getCapsuleById(capsuleId) {
    for (let index in capsules) {
        if (capsules[index].id === capsuleId) {
            return capsules[index];
        }
    }
    return undefined;
}