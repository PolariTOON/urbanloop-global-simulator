"""
Cette classe gère un réseau entier, c'est le niveau meta-graph du réseau
les noeuds peuvent être des routes (partie interne d'une boucle) ou des ponts (pour relier les boucles)
"""
from model.networks.lines.bridge import Bridge
from model.networks.roads.switch import Switch
from model.networks.roads.switch_in import SwitchIn
from ..node2 import Node


class Network(Node):
    def __init__(self, json_network):
        super().__init__()
        self._bridges = []
        self._loops = []
        self._roads = []
        self.init_graph_from_json(json_network)

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

    def init_graph_from_json(self, json_network):
        #  Etape 1 : Récupérer les infos du json sous forme pratique
        bridges = [{} for b in json_network["bridges"]]
        loops = [{} for l in json_network["loops"]]
        for loop in loops:
            loop["switches"] = []
            loop["routes"] = []
            steps = []
            for noeud in loop["elements"]:
                if noeud is Switch:
                    id_bridge = noeud["id_bridge"]
                    if noeud is SwitchIn:
                        if bridges[id_bridge]["in"] is None:
                            bridges[id_bridge]["in"] = [loop, len(loop["switches"])]
                        else:
                            print("[ERROR] MISTAKES IN THE NETWORK DESIGN")
                    else:
                        if bridges[id_bridge]["out"] is None:
                            bridges[id_bridge]["out"] = [loop, len(loop["switches"])]
                        else:
                            print("[ERROR] MISTAKES IN THE NETWORK DESIGN")
                    loop["switches"].append(noeud)
                    loop["routes"].append(steps)
                    steps = []
                else:
                    steps.append(noeud)
            if len(steps) != 0:
                loop["routes"].append(steps)

        #  Etape 2 : Instanciation des routes
        all_routes = []
        for loop in loops:
            for route in range(len(loop["routes"])):
                #  TODO : finir d'implémenter l'algo

