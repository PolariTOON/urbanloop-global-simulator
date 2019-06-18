"""
Cette classe gère un réseau entier, c'est le niveau meta-graph du réseau
les noeuds peuvent être des routes (partie interne d'une boucle) ou des ponts (pour relier les boucles)
"""
from model.networks.lines.bridge import Bridge
from model.networks.lines.loop import Loop
from model.networks.roads.route import Route
from model.networks.roads.switch import Switch
from ..node2 import Node


class Network(Node):
    def __init__(self, json_network):
        super().__init__()
        self._bridges = []
        self._loops = []
        self._switches = []
        self._routes = []
        self.init_graph_from_json(json_network)

    @property
    def capsules(self):
        return [capsule for capsule in self._routes] + [capsule for capsule in self._bridges]

    @property
    def bridges(self):
        return self._bridges

    @property
    def loops(self):
        return self._loops

    def serialize(self):
        return super().serialize().update({
            'bridges': [bridge.serialize() for bridge in self._bridges],
            'loops': [loop.serialize() for loop in self._loops],
        })

    def init_graph_from_json(self, json_network):
        #  Etape 1 : Récupérer les infos du json sous forme pratique
        bridges = json_network["bridges"]
        loops = json_network["loops"]
        for b in range(json_network["loops"]):
            loops[b]["switches"] = []
            loops[b]["routes"] = []
            steps = []
            paths = []
            for node in range(len(json_network["loops"][b]["elements"])):
                n = loops[b]["elements"][node]
                p = loops[b]["paths"][node]
                if "switch" in n["type"]:
                    id_bridge = n["id_bridge"]
                    if n["type"] == "switch_in":
                        if not bridges[id_bridge]["in"]:
                            bridges[id_bridge]["in"] = [loops[b], len(loops[b]["switches"])]  # [id_boucle, id_switch_in]
                        else:
                            print("[ERROR] MISTAKES IN THE NETWORK DESIGN")
                    else:
                        if not bridges[id_bridge]["out"]:
                            bridges[id_bridge]["out"] = [loops[b], len(loops[b]["switches"])]  # [id_boucle, id_switch_out]
                        else:
                            print("[ERROR] MISTAKES IN THE NETWORK DESIGN")
                    loops[b]["switches"].append(n)
                    loops[b]["routes"].append({"steps": steps, "paths": paths})
                    steps = []
                else:
                    steps.append(n)
                paths.append(p)
            if len(steps) != 0:
                loops[b]["routes"].append({"steps": steps, "paths": paths})

        #  Etape 2 : Instanciation des routes
        all_routes = []
        for b in range(len(loops)):
            for route in range(1, len(loops[b]["routes"])):
                new_route = Route(len(all_routes), loops[b]["routes"][route])
                all_routes.append(new_route)
                #  Comme le premier elt est une liste vide on remet les elts en remplaçant celle-ci
                loops[b]["routes"][route - 1]["steps"] = new_route
            loops[b]["routes"].pop()
        l = len(all_routes)  # nombre de routes du réseau internes aux boucles
        for p in range(len(bridges)):
            new_route = Route(l + p, [], bridges[p])
            all_routes.append(new_route)
            bridges[p]["route"] = new_route  # On ajoute sa route au bridge

        #  Etape 3 : Instanciation des aiguillages et liaison avec les routes
        all_switches = []
        for b in range(len(loops)):
            for s in range(len(loops[b]["switches"])):
                id_switch = len(all_switches)
                route1 = all_routes[(id_switch - 1) % len(loops[b]["switches"])]
                route2 = all_routes[id_switch]
                route3 = all_routes[l + loops[b]["switches"][s]["id_bridge"]]
                new_switch = Switch(id_switch, route1, route2, route3)
                all_switches.append(new_switch)
                loops[b]["switchs"][s] = new_switch

        #  Etape 4 : Instanciation des boucles et des ponts (sert pour la vue)
        for p in range(len(bridges)):
            b, s = bridges[p]["in"]
            bridges[p]["in"] = loops[b]["switches"][s]
            b, s = bridges[p]["out"]
            bridges[p]["out"] = loops[b]["switches"][s]
            bridges[p] = Bridge(bridges[p]["in"], bridges[p]["out"], bridges[p]["route"], bridges[p])
        for b in range(len(loops)):
            loops[b] = Loop(loops[b]["routes"], loops[b]["switches"], loops[b]["name"],
                            loops[b]["paths"])

        # Etape 5 : On donne le résultat de l'algorithme en attribut du réseau
        self._loops = loops
        self._bridges = bridges
        self._switches = all_switches
        self._routes = all_routes
