# global
capsuleId = 0
stationId = 0

class Loop:
  def __init__(self, name, stations = None):
    self.name = name
    self.stations = stations

class Station:
  # capsules
  capsulesInSlots = None
  # network
  network = None

  def __init__(self, name = None, capacity = 1, previousStation = None, nextStation = None, loop = None):
    global stationId
    # properties
    self.name = "Station #{0}".format(stationId) if name == None else name
    self.capacity = capacity
    self.previousStation = previousStation
    self.nextStation = nextStation
    self.loop = loop
    stationId+=1
  
  def _updateFlow(self):
    print("updating flow...")
    return
  
  def showDetails(self):
    print("showing details...")
    return

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
  securityDistance = 5000 # millimeters
  releaseTime = 12345 # miilisec
  accelerationTime = 12345 # miilisec
  maxSpeed = 22.2 # m/s (80km/h)
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

class Destination:
  def __init__(self, station, distance, cost):
    self.station = station
    self.distance = distance
    self.cost = cost # estimated time cost
  
  def updateCost(self):
    # TODO
    return

class Switch:
  # network
  network = None
  isRoutingToLoop = False

  def __init__(self, loop, nextStops):
    self.loop = loop
    self.nextStops = nextStops
  
  def _changeState(self):
    self.isRoutingToLoop = not self.isRoutingToLoop
    return
  
  def routeCapsuleToStation(self, capsule, station):
    # TODO
    return
