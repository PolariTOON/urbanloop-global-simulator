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
        for b in range(len(self._loops)):
            self._loops[b]["switches"] = []
            self._loops[b]["routes"] = []
            steps = []
            sections = []
            for node in range(len(self._loops[b]["elements"])):
                n = self._loops[b]["elements"][node]
                p = self._loops[b]["paths"][node]
                if n["type"] in ["switch_in", "switch_out"]:
                    id_bridge = n["id_bridge"]
                    if n["type"] == "switch_in":
                        if "in" in self._bridges[id_bridge]:
                            raise ValueError("[ERROR] MISTAKES IN THE NETWORK DESIGN")
                        self._bridges[id_bridge]["switch_in"] = {
                            "loop": b,
                            "element": node
                        }
                    else:
                        if "out" in self._bridges[id_bridge]:
                            raise ValueError("[ERROR] MISTAKES IN THE NETWORK DESIGN")
                        self._bridges[id_bridge]["switch_out"] = {
                            "loop": b,
                            "element": node
                        }
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
            self._bridges[p]["routes"] = [new_route]  # On ajoute sa route au bridge

        #  Etape 3 : Instanciation des aiguillages, ajout de leurs capsules et liaison avec les routes
        for b in range(len(self._loops)):
            for s in range(len(self._loops[b]["switches"])):
                #  Capsules
                pods = self._loops[b]["switches"][s]["pods"]
                for pod_branch_key in pods:
                    pod_branch = pods[pod_branch_key]
                    for pod_index in range(len(pod_branch)):
                        pod = self._loops[b]["switches"][s]["pods"][pod_index]
                        pod["source"] = self._get_elt_of_loop(**pod["source"])
                        pod["destination"] = self._get_elt_of_loop(**pod["destination"])
                        pod_branch[pod_index] = Pod(**pod)  # TODO: instancier les pods directement dans les switches ?
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
            bridge = self._bridges[p]
            switch_out = self._get_elt_of_loop(**bridge["switch_out"])
            switch_in = self._get_elt_of_loop(**bridge["switch_in"])
            bridge["switches"] = [switch_out, switch_in]
            self._init_pods_of_line(bridge)
            self._bridges[p] = Bridge(**bridge)
        for b in range(len(self._loops)):
            loop = self._loops[b]
            self._init_pods_of_line(loop)
            self._loops[b] = Loop(**loop)

    def _init_pods_of_line(self, line):
        for pod in line["pods"]:
            pod["source"] = self._get_elt_of_loop(**pod["source"])
            pod["destination"] = self._get_elt_of_loop(**pod["destination"])
            self._init_pod_of_line(line, pod)

    def _init_pod_of_line(self, line, pod):
        position = pod["position"]
        if position < 0:
            raise ValueError("Element's position out of range")
        for route in line["routes"]:
            for section in route.sections:
                length = section.length
                if position < length:
                    pod["position"] = position
                    section.insert_pod(**pod)
                    return
                position -= length
        raise ValueError("Element's position out of range")

    def _get_elt_of_loop(self, loop=None, element=None):
        """
        :param source_dest: dictionnaire obtenu à partir du fichier json
        de la forme {"loop": id_loop, "element": id_element}
        :return: l'objet instancié correspondant au numéro d'élément présent dans la boucle spécifiée
        """
        #  Initialisation des variables
        if loop < 0 or loop > len(self._loops):
            raise ValueError("Loop's index out of range")
        loop = self._loops[loop]
        routes = loop["routes"]
        switches = loop["switches"]
        if element < 0:
            raise ValueError("Element's index out of range")
        elt = 0
        #  Recherche du noeud
        for r in range(len(routes)):
            if elt == element:  # L'element est un switch
                return switches[r]
            elt += 1
            steps = routes[r].steps
            for s in range(len(steps)):
                if elt == element:  # L'element est une etape
                    return steps[s]
                elt += 1
        raise ValueError("Element's index out of range")
