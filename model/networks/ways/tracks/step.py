"""
Classe abstraite représentant les noeuds des sous-graphes du réseau
"""

from .track import Track


class Step(Track):
    def __init__(self, angle):
        super().__init__(angle)
        self._angle = angle

    @property
    def angle(self):
        return self._angle

    def serialize(self):
        return super().serialize().update({
            'angle': self.angle
        })
