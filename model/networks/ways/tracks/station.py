"""
Type de noeud du sous-graphe correspondant à une station d"arrêt
"""

from enum import Enum
from ...tokens.capsule import Capsule
from .step import Step


class Type(Enum):
    ACTIVITY = 1
    RESIDENTIAL = 2
    CITY = 3


class Station(Step):
    def __init__(self, capsules=None, station_type=None, **kwargs):
        super().__init__(**kwargs)
        capsules = capsules or {
            "count": 0,
            "max": 0
        }
        self._capsules = [Capsule() for k in range(capsules["count"])]
        self._capacity = capsules["max"] or 0
        self._station_type = station_type

    def serialize(self):
        return super().serialize().update({
            "type": "station",
            "capsules": {
                "count": len(self._capsules),
                "max": self._capacity
            },
            "station_type": self._station_type
        })
