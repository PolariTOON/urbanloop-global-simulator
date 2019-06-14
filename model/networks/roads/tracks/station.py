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
    def __init__(self):
        super().__init__(self)

    def serialize():
        return super().serialize().update({
            'type': 'station'
        })
