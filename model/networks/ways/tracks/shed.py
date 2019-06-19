"""
Type de noeud du sous-graphe du réseau qui représente un garage où sont stocker des capsules
"""

from ...tokens.capsule import Capsule
from .step import Step


class Shed(Step):
    def __init__(self, capsules=None, **kwargs):
        super().__init__(**kwargs)
        capsules = capsules or {
            "count": 0,
            "max": 0
        }
        self._capsules = [Capsule() for k in range(capsules["count"])]
        self._capacity = capsules["max"] or 0

    def serialize(self):
        return super().serialize().update({
            "type": "shed",
            "capsules": {
                "count": len(self._capsules),
                "max": self._capacity
            }
        })
