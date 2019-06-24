"""
Type de noeud du sous-graphe du réseau qui représente un garage où sont stocker des pods
"""

from ...tokens.pod import Pod
from .step import Step


class Shed(Step):
    def __init__(self, id, pods=None, element_of_loop=None, **kwargs):
        super().__init__(id, **kwargs)
        pods = pods or {
            "count": 0,
            "max": 0
        }
        pods["count"] = pods["count"] or 0
        pods["max"] = pods["max"] or 0
        element_of_loop = element_of_loop or {
            "loop": 0,
            "element": 0
        }
        element_of_loop["loop"] = element_of_loop["loop"] or 0
        element_of_loop["element"] = element_of_loop["element"] or 0
        self._pods = [Pod() for k in range(pods["count"])]
        self._capacity = pods["max"]
        self._element_of_loop = element_of_loop

    def serialize(self):
        dict = super().serialize()
        dict.update({
            "type": "shed",
            "pods": {
                "count": len(self._pods),
                "max": self._capacity
            }
        })
        return dict

    def to_element_of_loop(self):
        return self._element_of_loop

    @property
    def pods(self):
        return self._pods
