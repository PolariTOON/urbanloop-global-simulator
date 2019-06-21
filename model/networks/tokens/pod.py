from uuid import uuid4
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
        self._travelers = [Traveler(source, destination) for k in range(travelers["count"])]
        self._capacity = travelers["max"]

    @property
    def poosition(self):
        return self._position

    @property
    def travelers(self):
        return self._travelers

    def serialize(self):
        return super().serialize().update({
            "position": self._position,
            "travelers": {
                "count": len(self._travelers),
                "max": self._capacity
            }
        })
