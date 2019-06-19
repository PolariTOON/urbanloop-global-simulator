"""
Type de noeud du sous-graphe du réseau qui représente un garage où sont stocker des capsules
"""

from .step import Step


class Shed(Step):
    def __init__(self, name, capacity, pod_count, x, y):
        super().__init__()
        self.name = name
        self.capacity = capacity
        self.pod_count = pod_count
        self.x = x
        self.y = y

    def serialize(self):
        return super().serialize().update({
            'type': 'warehouse'
        })
