import Model.Global

stationId = Model.Global.stationId

class Capsule:
    # capsule data
    isMoving = False
    isLoaded = False
    currentStation = None
    nextSwitch = None
    finalDestination = None
    velocity = 0
    acceleration = 0
    # parameters to inject
    securityDistance = 5000  # millimeters
    releaseTime = 12345  # miilisec
    accelerationTime = 12345  # miilisec
    maxSpeed = 22.2  # m/s (80km/h)
    # network data
    networkMap = None
    network = None

    def __init__(self, name, station):
        global capsuleId
        self.name = "Capsule #{0}".format(stationId) if name == None else name
        self.currentStation = station

    def _startMovingTo(self, station):
        # TODO
        return

    def _enterInto(self, station):
        # TODO
        return

    def _hasArrivedTo(self, station):
        # TODO
        return

    def _prepareLeaving(self, station):
        # TODO
        return

    def _leave(self, station):
        # TODO
        return

    def _insertionIntoLoop(self):
        # TODO
        return

    def _changeLoop(self, station):
        # TODO
        return

    def _doALoop(self, station):
        # TODO
        return

    def _refreshMap(self):
        # TODO
        return

    def showDetails(self, station):
        # TODO
        return
