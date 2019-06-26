"""
Type de noeud du sous-graphe correspondant à une station d"arrêt
"""

from enum import Enum
from ...tokens.pod import Pod
from .step import Step


class Type(Enum):
    ACTIVITY = 0
    RESIDENTIAL = 1
    CITY = 2


class Station(Step):
    def __init__(self, id, pods=None, travelers=None, station_type=None, element_of_loop=None, **kwargs):
        super().__init__(id, **kwargs)
        pods = pods or {
            "count": 0,
            "max": 0
        }
        pods["count"] = pods["count"] or 0
        pods["max"] = pods["max"] or 0
        travelers = travelers or 0
        station_type = station_type or Type.CITY
        element_of_loop = element_of_loop or {
            "loop": 0,
            "element": 0
        }
        element_of_loop["loop"] = element_of_loop["loop"] or 0
        element_of_loop["element"] = element_of_loop["element"] or 0
        self._pods = [Pod() for k in range(pods["count"])]
        self._capacity = pods["max"]
        self._travelers = travelers
        self._station_type = station_type
        self._element_of_loop = element_of_loop

    def serialize(self):
        dict = super().serialize()
        dict.update({
            "type": "station",
            "pods": {
                "count": len(self._pods),
                "max": self._capacity
            },
            "travelers": self._travelers,
            "station_type": self._station_type,
        })
        return dict

    def to_element_of_loop(self):
        return self._element_of_loop

    @property
    def pods(self):
        return self._pods

    @property
    def travelers(self):
        return self._travelers

    @property
    def type(self):
        return self._station_type
