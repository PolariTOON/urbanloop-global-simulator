"""
Type de noeud du sous-graphe correspondant à une station d'arrêt
"""
from enum import Enum


class Type(Enum):
    ACTIVITY = 1
    RESIDENTIAL = 2
    CITY = 3