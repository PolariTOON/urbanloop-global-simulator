"""
Type de noeud du sous-graphe du réseau qui représente un garage où sont stocker des pods
"""

from ...tokens.pod import Capsule
from .step import Step


class Shed(Step):
    def __init__(self, pods=None, **kwargs):
        super().__init__(**kwargs)
        pods = pods or {
            "count": 0,
            "max": 0
        }
        self._pods = [Capsule() for k in range(pods["count"])]
        self._capacity = pods["max"] or 0

    def serialize(self):
        return super().serialize().update({
            "type": "shed",
            "pods": {
                "count": len(self._pods),
                "max": self._capacity
            }
        })
