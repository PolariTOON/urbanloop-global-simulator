class Station:
    # capsules
    capsulesInSlots = None
    # network
    network = None

    def __init__(self, name=None, capacity=1, previousStation=None, nextStation=None, loop=None):
        global stationId
        # properties
        self.name = "Station #{0}".format(stationId) if name == None else name
        self.capacity = capacity
        self.previousStation = previousStation
        self.nextStation = nextStation
        self.loop = loop
        stationId += 1

    def _updateFlow(self):
        print("updating flow...")
        return

    def showDetails(self):
        print("showing details...")
        return