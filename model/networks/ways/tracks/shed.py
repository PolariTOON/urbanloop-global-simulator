"""
Type de noeud du sous-graphe du réseau qui représente un garage où sont stocker des pods
"""

from ...tokens.pod import Pod
from .step import Step


class Shed(Step):
    def __init__(self, previous_track, next_track, pods=None, **kwargs):
        super().__init__(previous_track, next_track, **kwargs)
        pods = pods or {
            "count": 0,
            "max": 0
        }
        self._pods = [Pod() for k in range(pods["count"])]
        self._capacity = pods["max"] or 0

    def serialize(self):
        return super().serialize().update({
            "type": "shed",
            "pods": {
                "count": len(self._pods),
                "max": self._capacity
            }
        })
