"""
Type de noeud du sous-graphe correspondant à une station d'arrêt
"""

from enum import Enum
from .route_node import RouteNode


class Type(Enum):
    ACTIVITY = 1
    RESIDENTIAL = 2
    CITY = 3


class Station(RouteNode):
    def __init__(self):
        pass

    def serialize():
        return super().serialize().update({
            'jsonType': 'station'
        })
