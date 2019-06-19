"""
Type de noeud du sous-graphe correspondant à une station d"arrêt
"""

from enum import Enum
from ...tokens.pod import Capsule
from .step import Step


class Type(Enum):
    ACTIVITY = 1
    RESIDENTIAL = 2
    CITY = 3


class Station(Step):
    def __init__(self, pods=None, station_type=None, **kwargs):
        super().__init__(**kwargs)
        pods = pods or {
            "count": 0,
            "max": 0
        }
        self._pods = [Capsule() for k in range(pods["count"])]
        self._capacity = pods["max"] or 0
        self._station_type = station_type

    def serialize(self):
        return super().serialize().update({
            "type": "station",
            "pods": {
                "count": len(self._pods),
                "max": self._capacity
            },
            "station_type": self._station_type
        })
