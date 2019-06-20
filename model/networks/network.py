"""
Cette classe gère un réseau entier, c'est le niveau meta-graph du réseau
les noeuds peuvent être des routes (partie interne d'une boucle) ou des ponts (pour relier les boucles)
"""
from model.networks.tokens.pod import Pod
from model.networks.tokens.traveler import Traveler
from ..node2 import Node
from .lines.bridge import Bridge
from .lines.loop import Loop
from .ways.route import Route
from .ways.switch_in import SwitchIn
from .ways.switch_out import SwitchOut


class Network(Node):
    def __init__(self, bridges=None, loops=None, switches=None, routes=None, **kwargs):
        super().__init__(**kwargs)
        self._bridges = bridges or []
        self._loops = loops or []
        self._switches = switches or []
        self._routes = routes or []
        self._init_graph_from_json()

    @property
    def pods(self):
        return [pod for pod in self._routes] + [pod for pod in self._bridges]

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
            sections = []
            for node in range(len(self._loops[b]["elements"])):
                n = self._loops[b]["elements"][node]
                p = self._loops[b]["paths"][node]
                if "switch" in n["type"]:
                    id_bridge = n["id_bridge"]
                    if n["type"] == "switch_in":
                        if not self._bridges[id_bridge]["in"]:
                            self._bridges[id_bridge]["in"] = [self._loops[b], len(
                                self._loops[b]["switches"])]  # [id_boucle, id_switch_in]
                        else:
                            print("[ERROR] MISTAKES IN THE NETWORK DESIGN")
                    else:
                        if not self._bridges[id_bridge]["out"]:
                            self._bridges[id_bridge]["out"] = [self._loops[b], len(
                                self._loops[b]["switches"])]  # [id_boucle, id_switch_out]
                        else:
                            print("[ERROR] MISTAKES IN THE NETWORK DESIGN")
                    self._loops[b]["switches"].append(n)
                    self._loops[b]["routes"].append({"steps": steps, "sections": sections})
                    steps = []
                    sections = []
                else:
                    if n["type"] == "station" or n["type"] == "shed":
                        # Ajout des capsules sans voyageurs
                        pods_sc = []
                        for c in range(n["pods"]["count"]):
                            pods_sc.append(Pod(None, None))
                        n["pods_list"] = pods_sc
                    steps.append(n)  # important : on ajoute l'étape
                sections.append(p)
            if len(steps) != 0:
                self._loops[b]["routes"].append({"steps": steps, "sections": sections})

        #  Etape 2 : Instanciation des routes
        for b in range(len(self._loops)):
            for route in range(1, len(self._loops[b]["routes"])):
                new_route = Route(len(self._routes),
                                  **self._loops[b]["routes"][route])  # Ici se fait la liaison des pistes (sections internes et étapes) : étape 42
                self._routes.append(new_route)
                #  Comme le premier elt est une liste vide on remet les elts en remplaçant celle-ci
                self._loops[b]["routes"][route - 1]["steps"] = new_route
                self._loops[b]["routes"][route - 1]["sections"] = self._loops[b]["routes"][route]["sections"]
            self._loops[b]["routes"].pop()
        l = len(self._routes)  # nombre de routes du réseau internes aux boucles
        for p in range(len(self._bridges)):
            steps = []
            sections = [self._bridges[p]["path"]]
            new_route = Route(l + p, **{"steps": steps, "sections": sections})  # La liaison se fait au niveau de l'instanciation des switches (plus tard dans l'algo)
            self._routes.append(new_route)
            self._bridges[p]["route"] = new_route  # On ajoute sa route au bridge

        #  Etape 3 : Instanciation des aiguillages, ajout de leurs capsules et liaison avec les routes
        for b in range(len(self._loops)):
            for s in range(len(self._loops[b]["switches"])):
                #  Capsules
                for branch_key in self._loops[b]["switches"][s]["pods"]:
                    branch_value = self._loops[b]["switches"][s]["pods"][branch_key]
                    for pod in range(len(branch_value)):
                        source = self._get_elt_of_loop(self._loops[b]["switches"][s]["pods"][pod]["source"])
                        destination = self._get_elt_of_loop(self._loops[b]["switches"][s]["pods"][pod]["destination"])
                        travelers = []
                        for _ in range(self._loops[b]["switches"][s]["pods"][pod]["travelers"]["count"]):
                            travelers.append(Traveler(source, destination))
                        new_pod = Pod(source, destination, travelers)
                        self._loops[b]["switches"][s]["pods"][branch_key] = new_pod
                #  Routes et Id
                id_switch = len(self._switches)
                route_in = self._routes[(id_switch - 1) % len(self._loops[b]["switches"])]
                route_out = self._routes[id_switch]
                route_bridge = self._routes[l + self._loops[b]["switches"][s]["id_bridge"]]
                if self._loops[b]["switches"][s]["type"] == "switch_in":
                    new_switch = SwitchIn(id_switch, self._loops[b]["switches"][s]["pods"], route_in, route_out, route_bridge)
                    # new_switch = SwitchIn(id_switch, **self._loops[b]["switches"][s]) : TODO : doit devenir comme ça
                else:
                    new_switch = SwitchOut(id_switch, self._loops[b]["switches"][s]["pods"], route_in, route_out, route_bridge)
                self._switches.append(new_switch)
                self._loops[b]["switches"][s] = new_switch

        #  Etape 4 : Instanciation des boucles et des ponts (sert pour la vue)
        for p in range(len(self._bridges)):
            b, s = self._bridges[p]["in"]
            self._bridges[p]["in"] = self._loops[b]["switches"][s]
            b, s = self._bridges[p]["out"]
            self._bridges[p]["out"] = self._loops[b]["switches"][s]
            self._bridges[p] = Bridge(**self._bridges[p])
        for b in range(len(self._loops)):
            self._loops[b] = Loop(**self._loops[b])

    def _get_elt_of_loop(self, source_dest):
        """
        :param source_dest: dictionnaire obtenu à partir du fichier json
        de la forme {"loop": id_loop, "element": id_element}
        :return: l'objet instancié correspondant au numéro d'élément présent dans la boucle spécifiée
        """
        #  Initialisation des variables
        b = source_dest["loop"]
        e = source_dest["element"]
        if e < 0:
            raise ValueError("Element's index must be positive")
        elt = 0
        #  Recherche du noeud
        for r in range(len(self._loops[b]["routes"])):
            if elt == e:  # L'element est un switch
                return self._loops[b]["switches"][r]
            elt += 1
            for s in range(len(self._loops[b]["routes"][r].steps)):
                if elt == e:  # L'element est une etape
                    return self._loops[b]["routes"][r].steps[s]
                elt += 1
        raise ValueError("Element's index out of the range of elements in the loop")

