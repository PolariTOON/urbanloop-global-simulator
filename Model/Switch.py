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
