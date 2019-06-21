"""
Classe abstraite représentant les noeuds des sous-graphes du réseau
"""

from .track import Track


class Step(Track):
    def __init__(self, x=None, y=None, previous=None, next=None, **kwargs):
        super().__init__(**kwargs)
        self._x = x or 0
        self._y = y or 0
        self._previous = previous or None
        self._next = next or None

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def previous(self):
        return self._previous

    @property
    def next(self):
        return self._next

    def serialize(self):
        return super().serialize().update({
            "x": self.x,
            "y": self.y
        })
