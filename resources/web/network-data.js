let loops = [];
let stations = [];
let switches = [];
let capsules = [];

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
        this.loopId = capsuleJSON['loopId'];
        /* An element is a switch or a station */
        this.elementId = capsuleJSON['elementId'];
        this.segmentPercentage = capsuleJSON['segmentPercentage'];
        this.travelerNumber = capsuleJSON['travelerNumber'];
        this.object = new CapsuleObject(this);
    }

    isAboard() {
        return this.travelerNumber > 0;
    }
}

function initData() {
    $.when(
        $.ajax($.get('/load'))
    ).then(
        $.when(
            $.ajax(
                $.get('/loops', function (listLoopJSON) {
                    listLoopJSON.forEach(function (loopJSON) {
                        loops.push(new Loop(loopJSON));
                    });
                })
            )
        ).then(
            $.when(
                $.ajax(
                    $.get('/stationsSetData', function (listStationSetDataJSON) {
                        listStationSetDataJSON.forEach(function (stationSetDataJSON) {
                            stations.push(new Station(new StationSetData(stationSetDataJSON)));
                        });
                    })
                )
            ).then(
                $.get('/switchesSetData', function (listSwitchSetDataJSON) {
                    listSwitchSetDataJSON.forEach(function (switchSetDataJSON) {
                        switches.push(new Switch(new SwitchSetData(switchSetDataJSON)));
                    });
                })
            )
        )
    );
}

function updateData(listStationVarDataJSON, listSwitchVarDataJSON, listCapsuleJSON) {
    updateStations(listStationVarDataJSON);
    updateSwitches(listSwitchVarDataJSON);
    updateCapsules(listCapsuleJSON);
}

function updateStations(listStationVarDataJSON) {
    listStationVarDataJSON.forEach(function (stationVarDataJSON) {
        getStationById(stationVarDataJSON['id']).update(stationVarDataJSON);
    });
}

function updateSwitches(listSwitchVarDataJSON) {
    listSwitchVarDataJSON.forEach(function (switchVarDataJSON) {
        getSwitchById(switchVarDataJSON['id']).update(switchVarDataJSON);
    });
}

function updateCapsules(listCapsuleJSON) {
    capsules = [];

    listCapsuleJSON.forEach(function (capsuleJSON) {
        capsules.push(new Capsule(capsuleJSON));
    });
}


function getStationById(stationId) {
    stations.forEach(function (a_station) {
        if (a_station.id === stationId) {
            return a_station;
        }
    });

    return null;
}

function getSwitchById(switchId) { // TODO FOREACH MARCHE PAS
    switches.forEach(function (a_switch) {
        if (a_switch.id === switchId) {
            return a_switch;
        }
    });

    return null;
}

function getLoopById(loopId) {  // TODO change name by id
    for (let index in loops) {
        if (loops[index].name === loopId) {
            return loops[index];
        }
    }
}