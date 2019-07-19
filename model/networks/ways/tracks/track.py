"""
Classe abstraite représentant les noeuds des sous-graphes du réseau
"""

from ....node2 import Node


class Track(Node):
    def __init__(self, env, id, **kwargs):
        super().__init__(env, id, **kwargs)

    @property
    def pods(self):
        raise NotImplementedError()

    @property
    def previous(self):
        raise NotImplementedError()

    @property
    def next(self):
        raise NotImplementedError()

    @property
    def length(self):
        return 0

    def serialize(self):
        dict = super().serialize()
        dict.update({})
        return dict
