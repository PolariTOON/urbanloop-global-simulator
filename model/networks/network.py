"""
Cette classe gère un réseau entier, c'est le niveau meta-graph du réseau
les noeuds peuvent être des routes (partie interne d'une boucle) ou des ponts (pour relier les boucles)
"""
import json

from ..node2 import Node


class Network(Node):
    def __init__(self, json_network_path):
        self._bridges = []
        self._loops = []
        self._roads = []

    @property
    def capsules(self):
        return [capsule for road in self._roads for capsule in road.capsules]

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

    def init_graph_from_json(self, json_network_path):
        with open(json_network_path) as json_data:
            json_network = json.load(json_data)
        loops = json_network["loops"]
        bridges = json_network["bridges"]
        capsules = json_network["capsules"]
        for bridge in bridges:
            path = bridge["type"]
            # TODO : charger les bridges
            new_bridge = Bridge()
            self._bridges.append(new_bridge)

        for loop in loops:
            loop_name = loop["name"]
            clockwise = loop["clockwise"]
            elements = loop["elements"]
            paths = loop["paths"]
            # TODO : charger les boucles
            new_loop = Loop()
            self._loops.append(new_loop)

        for capsule in capsules:
            # TODO : charger les capsules
            new_capsule = Capsule()
            for loop in self._loops:
                if new_capsule.loop_id == loop.id:
                    loop._capsules.append(new_capsule)
            pass
