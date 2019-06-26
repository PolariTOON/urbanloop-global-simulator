from uuid import uuid4

from settings import simlog
from .token import Token
from .traveler import Traveler


class Pod(Token):
    def __init__(self, position=None, travelers=None, **kwargs):
        super().__init__(**kwargs)
        self._id = uuid4().hex  # génération d'un identifiant unique
        self._position = position
        travelers = travelers or {
            "count": 0,
            "max": 0
        }
        travelers["count"] = travelers["count"] or 0
        travelers["max"] = travelers["max"] or 0
        source = self.source
        destination = self.destination
        self._travelers = [Traveler({
            "source": source,
            "destination": destination
        }) for k in range(travelers["count"])]
        self._capacity = travelers["max"]

    @property
    def position(self):
        return self._position

    @property
    def travelers(self):
        return self._travelers

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
        simlog.info("Traveler %s gets in capsule %d" % (traveler.id, self._id), traveler.source, self.destination)
