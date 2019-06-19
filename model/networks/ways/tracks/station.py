"""
Type de noeud du sous-graphe correspondant à une station d'arrêt
"""

from enum import Enum
from .step import Step


class Type(Enum):
    ACTIVITY = 1
    RESIDENTIAL = 2
    CITY = 3


class Station(Step):
    def __init__(self, name, capacity, capsule_count, station_type, x, y):
        super().__init__()
        self.name = name
        self.capacity = capacity
        self.capsule_count = capsule_count
        self.station_type = station_type
        self.x = x
        self.y = y

    def serialize(self):
        return super().serialize().update({
            'type': 'station'
        })
