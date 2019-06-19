"""
Cette classe gère un réseau entier, c'est le niveau meta-graph du réseau
les noeuds peuvent être des routes (partie interne d'une boucle) ou des ponts (pour relier les boucles)
"""

from ..node2 import Node
from .lines.bridge import Bridge
from .lines.loop import Loop
from .ways.route import Route
from .ways.switch_in import SwitchIn
from .ways.switch_out import SwitchOut


class Network(Node):
    def __init__(self, bridges=None, loops=None, switches=None, routes=None, capsules=None):
        super().__init__()
        self._bridges = bridges or []
        self._loops = loops or []
        self._switches = switches or []
        self._routes = routes or []
        self._init_graph_from_json()

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

    def _init_graph_from_json(self):
        #  Etape 1 : Récupérer les infos du json sous forme pratique
        for b in range(self._loops):
            self._loops[b]["switches"] = []
            self._loops[b]["routes"] = []
            steps = []
            paths = []
            for node in range(len(self._loops[b]["elements"])):
                n = self._loops[b]["elements"][node]
                p = self._loops[b]["paths"][node]
                if "switch" in n["type"]:
                    id_bridge = n["id_bridge"]
                    if n["type"] == "switch_in":
                        if not self._bridges[id_bridge]["in"]:
                            self._bridges[id_bridge]["in"] = [self._loops[b], len(self._loops[b]["switches"])]  # [id_boucle, id_switch_in]
                        else:
                            print("[ERROR] MISTAKES IN THE NETWORK DESIGN")
                    else:
                        if not self._bridges[id_bridge]["out"]:
                            self._bridges[id_bridge]["out"] = [self._loops[b], len(self._loops[b]["switches"])]  # [id_boucle, id_switch_out]
                        else:
                            print("[ERROR] MISTAKES IN THE NETWORK DESIGN")
                    self._loops[b]["switches"].append(n)
                    self._loops[b]["routes"].append({"steps": steps, "paths": paths})
                    steps = []
                else:
                    steps.append(n)
                paths.append(p)
            if len(steps) != 0:
                self._loops[b]["routes"].append({"steps": steps, "paths": paths})

        #  Etape 2 : Instanciation des routes
        for b in range(len(self._loops)):
            for route in range(1, len(self._loops[b]["routes"])):
                new_route = Route(len(self._routes), self._loops[b]["routes"][route])
                self._routes.append(new_route)
                #  Comme le premier elt est une liste vide on remet les elts en remplaçant celle-ci
                self._loops[b]["routes"][route - 1]["steps"] = new_route
            self._loops[b]["routes"].pop()
        l = len(self._routes)  # nombre de routes du réseau internes aux boucles
        for p in range(len(self._bridges)):
            new_route = Route(l + p, {"steps": [], "paths": [self._bridges[p]["path"]]})
            self._routes.append(new_route)
            self._bridges[p]["route"] = new_route  # On ajoute sa route au bridge

        #  Etape 3 : Instanciation des aiguillages et liaison avec les routes
        for b in range(len(self._loops)):
            for s in range(len(self._loops[b]["switches"])):
                id_switch = len(self._switches)
                route_in = self._routes[(id_switch - 1) % len(self._loops[b]["switches"])]
                route_out = self._routes[id_switch]
                route_bridge = self._routes[l + self._loops[b]["switches"][s]["id_bridge"]]
                if self._loops[b]["switches"][s]["type"] == "switch_in":
                    new_switch = SwitchIn(id_switch, route_in, route_out, route_bridge)
                else:
                    new_switch = SwitchOut(id_switch, route_in, route_out, route_bridge)
                self._switches.append(new_switch)
                self._loops[b]["switchs"][s] = new_switch

        #  Etape 4 : Instanciation des boucles et des ponts (sert pour la vue)
        for p in range(len(self._bridges)):
            b, s = self._bridges[p]["in"]
            self._bridges[p]["in"] = self._loops[b]["switches"][s]
            b, s = self._bridges[p]["out"]
            self._bridges[p]["out"] = self._loops[b]["switches"][s]
            self._bridges[p] = Bridge(self._bridges[p]["in"], self._bridges[p]["out"], self._bridges[p]["route"], self._bridges[p])
        for b in range(len(self._loops)):
            self._loops[b] = Loop(self._loops[b]["routes"], self._loops[b]["switches"], self._loops[b]["name"],
                            self._loops[b]["paths"])
