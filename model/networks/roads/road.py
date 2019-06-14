"""
Classe abstraite liée à un noeud du meta-graphe représentant le réseau dans sa globalité
"""

from ...node2 import Node


class Road(Node):
    def __init__(self):
        super().__init__(self)
        self._previous_road = None
        self._next_road = None

    def serialize():
        return super().serialize().update({})
