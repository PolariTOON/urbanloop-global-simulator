from uuid import uuid4
from .token import Token
from .traveler import Traveler


class Pod(Token):
    def __init__(self, source=None, destination=None, travelers=None):
        super().__init__(source, destination)
        self._id = uuid4().hex  # génération d'un identifiant unique
        self._source = source
        self._destination = destination
        travelers = travelers or {
            "count": 0,
            "max": 0
        }
        self._travelers = [Traveler(source, destination) for k in range(travelers["count"])]
        self._capacity = travelers["max"] or 0

    @property
    def travelers(self):
        return self._travelers

    def serialize(self):
        return super().serialize().update({
            'travelers': [traveler.serialize() for traveler in self.travelers]
        })
