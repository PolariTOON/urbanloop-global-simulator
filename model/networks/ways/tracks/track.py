"""
Classe abstraite représentant les noeuds des sous-graphes du réseau
"""

from ....node2 import Node


class Track(Node):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def pods(self):
        raise NotImplementedError()

    @property
    def previous(self):
        raise NotImplementedError()

    @property
    def next(self):
        raise NotImplementedError()

    def serialize(self):
        return super().serialize().update({})
