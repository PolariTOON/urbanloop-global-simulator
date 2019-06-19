"""
Classe abstraite représentant les noeuds des sous-graphes du réseau
"""

from ....node2 import Node


class Track(Node):
    def __init__(self):
        super().__init__()
        self._previous_track = None
        self._next_track = None
        self._pods = []  # TODO déplacer vers les sections et les différentes étapes

    @property
    def pods(self):
        return self._pods

    def serialize(self):
        return super().serialize().update({})
