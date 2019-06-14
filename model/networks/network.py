"""
Cette classe gère un réseau entier, c'est le niveau meta-graph du réseau
les noeuds peuvent être des routes (partie interne d'une boucle) ou des ponts (pour relier les boucles)
"""

from ..node import Node


class Network(Node):
    def __init__(self):
        self._bridges = []
        self._loops = []
        self._roads = []

    @property
    def capsules(self):
        return [capsule for road in self.roads for capsule in road.capsules]

    @property
    def bridges(self):
        return self._bridges

    @property
    def loops(self):
        return self._loops

    def serialize(self):
        return super().serialize().update({
            'bridges': [bridge.serialize() for bridge in self.bridges],
            'loops': [loop.serialize() for loop in self.loops],
        })

    def init_graph_from_json(self, json_network):
        for loop_name, info in json_network.items():
