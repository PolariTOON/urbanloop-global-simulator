"""
Classe abstraite représentant les noeuds des sous-graphes du réseau
"""

from ...node import Node


class RouteNode(Node):
    def __init__(self, angle):
        self._capsules = []
        self._angle = angle

    @property
    def capsules(self):
        return self._capsules

    def serialize(self):
        return super().serialize().update({
            'jsonType': 'route_node',
            'capsules': [capsule.serialize() for capsule in self.capsules]
        })
