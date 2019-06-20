"""
Classe abstraite représentant les noeuds des sous-graphes du réseau
"""

from .track import Track


class Step(Track):
    def __init__(self, previous_track, next_track, x=None, y=None, **kwargs):
        super().__init__(previous_track, next_track, **kwargs)
        self._x = x or 0
        self._y = y or 0

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    def serialize(self):
        return super().serialize().update({
            "x": self.x,
            "y": self.y
        })
