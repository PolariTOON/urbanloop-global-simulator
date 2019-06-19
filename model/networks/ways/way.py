"""
Classe abstraite liée à un noeud du meta-graphe représentant le réseau dans sa globalité
"""

from ...node2 import Node


class Way(Node):
    def __init__(self):
        super().__init__()
        self._previous_road = None
        self._next_road = None

    def serialize(self):
        return super().serialize().update({})

    @property
    def capsules(self):
        return NotImplementedError
