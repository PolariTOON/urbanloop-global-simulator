from settings import simlog
from .token import Token
from .traveler import Traveler


class Pod(Token):
    def __init__(self, track, position=None, travelers=None, **kwargs):
        super().__init__(**kwargs)
        self._position = position
        travelers = travelers or {
            "count": 0,
            "max": 0
        }
        travelers["count"] = travelers["count"] or 0
        travelers["max"] = travelers["max"] or 0
        source = self.source
        destination = self.destination
        self._travelers = [Traveler(0, {
            "source": source,
            "destination": destination
        }) for k in range(travelers["count"])]
        self._capacity = travelers["max"]
        self._priority = 0  # TODO
        self._track = track  # TODO

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        self._position = value

    @property
    def travelers(self):
        return self._travelers

    @travelers.setter
    def travelers(self, value):
        self._travelers = value

    @property
    def priority(self):
        return self._priority

    @priority.setter
    def priority(self, value):
        self._priority = value

    @property
    def track(self):
        return self._track

    @track.setter
    def track(self, value):
        self._track = value

    def serialize(self):
        dict = super().serialize()
        dict.update({
            "position": self._position,
            "travelers": {
                "count": len(self._travelers),
                "max": self._capacity
            }
        })
        return dict

    def add_traveler(self, traveler):
        self._travelers.append(traveler)
        simlog.info("Traveler %s gets in capsule %d" % (traveler.id, self.id), traveler.source, self.destination)
