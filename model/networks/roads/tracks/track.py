"""
Classe abstraite représentant les noeuds des sous-graphes du réseau
"""

from ....node2 import Node


class Track(Node):
    def __init__(self, angle):
        super().__init__(self)
        self._previous_track = None
        self._next_track = None
        self._capsules = [] # TODO déplacer vers les sections et les différentes étapes

    @property
    def capsules(self):
        return self._capsules

    def serialize(self):
        return super().serialize().update({})
