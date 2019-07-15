"""
Classe abstraite représentant les noeuds des sous-graphes du réseau
"""

from .track import Track


class Step(Track):
    def __init__(self, env, id, x=None, y=None, previous=None, next=None, **kwargs):
        super().__init__(env, id, **kwargs)
        self._x = x or 0
        self._y = y or 0
        self._previous = previous or None
        self._next = next or None
        self._previous.next = self
        self._next.previous = self

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
        dict = super().serialize()
        dict.update({
            "x": self._x,
            "y": self._y
        })
        return dict

    @property
    def pods(self):
        raise NotImplementedError
