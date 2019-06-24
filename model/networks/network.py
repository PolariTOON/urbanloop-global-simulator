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
    def __init__(self, id, bridges=None, loops=None, switches=None, routes=None, **kwargs):
        super().__init__(id, **kwargs)
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
        """
        Création du model à partir du dictionnaire obtenu à partir du fichier json
        :return: (void) Le réseau est construit
        """
        #  Etape 1 : Récupérer les infos du json sous forme pratique
        print("Etape 1 : ...")
        for b in range(len(self._loops)):
            self._loops[b]["switches"] = []
            self._loops[b]["routes"] = []
            steps = []
            sections = []
            elements = self._loops[b]["elements"]
            routes = self._loops[b]["routes"]
            for node in range(len(elements)):
                n = elements[node]
                p = self._loops[b]["sections"][node]
                if n["type"] in ["switch_in", "switch_out"]:
                    id_bridge = n["id_bridge"]
                    if n["type"] == "switch_in":
                        if "switch_in" in self._bridges[id_bridge]:
                            raise ValueError("[ERROR] MISTAKES IN THE NETWORK DESIGN")
                        self._bridges[id_bridge]["switch_in"] = {
                            "loop": b,
                            "element": node
                        }
                    else:
                        if "switch_out" in self._bridges[id_bridge]:
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
                        n["element_of_loop"] = {
                            "loop": b,
                            "element": node
                        }
                    steps.append(n)  # important : on ajoute l'étape
                sections.append(p)
            routes.append({"steps": steps, "sections": sections})
        print("Etape 1 : [OK]")
        print("Etape 2 : ...")
        #  Etape 2 : Instanciation des routes
        for b in range(len(self._loops)):
            routes = self._loops[b]["routes"]
            for route in range(1, len(routes)):
                print("creation route : id=", len(self._routes))
                new_route = Route(len(self._routes), **routes[route])  # Ici se fait la liaison des pistes (sections internes et étapes) : étape 42
                self._routes.append(new_route)
                #  Comme le premier elt est une liste vide on remet les elts en remplaçant celle-ci
                routes[route - 1] = new_route
            routes.pop()
        l = len(self._routes)  # nombre de routes du réseau internes aux boucles
        for p in range(len(self._bridges)):
            steps = []
            sections = [self._bridges[p]["section"]]
            new_route = Route(l + p, **{"steps": steps, "sections": sections})  # La liaison se fait au niveau de l'instanciation des switches (plus tard dans l'algo)
            self._routes.append(new_route)
            self._bridges[p]["routes"] = [new_route]  # On ajoute sa route au bridge
        print("Etape 2 : [OK]")
        print("Etape 3 : ...")
        #  Etape 3 : Instanciation des aiguillages, ajout de leurs capsules et liaison avec les routes
        for b in range(len(self._loops)):
            for s in range(len(self._loops[b]["switches"])):
                #  Capsules
                switch = self._loops[b]["switches"][s]
                pods = switch["pods"]
                for pod_branch_key in pods:
                    pod_branch = pods[pod_branch_key]
                    for pod_index in range(len(pod_branch)):
                        pod = self._loops[b]["switches"][s]["pods"][pod_index]
                        pod["source"] = self._get_elt_of_loop(**pod["source"])
                        pod["destination"] = self._get_elt_of_loop(**pod["destination"])
                #  Routes et Id
                id_switch = len(self._switches)
                switch["loop_in"] = self._routes[(id_switch - 1) % len(self._loops[b]["switches"])]  # loop_in
                switch["loop_out"] = self._routes[id_switch]  # loop_out
                switch["route_bridge"] = self._routes[l + switch["id_bridge"]]  # route_bridge
                if switch["type"] == "switch_in":
                    new_switch = SwitchIn(id_switch, **switch)
                else:
                    new_switch = SwitchOut(id_switch, **switch)
                self._switches.append(new_switch)
                self._loops[b]["switches"][s] = new_switch
        print("Etape 3 : [OK]")
        #  Etape 4 : Instanciation des boucles et des ponts (sert pour la vue)
        for p in range(len(self._bridges)):
            bridge = self._bridges[p]
            switch_out = self._get_elt_of_loop(**bridge["switch_out"])
            switch_in = self._get_elt_of_loop(**bridge["switch_in"])
            bridge["switches"] = [switch_out, switch_in]
            self._init_pods_of_line(bridge)
            self._bridges[p] = Bridge(p, **bridge)
        for b in range(len(self._loops)):
            loop = self._loops[b]
            self._init_pods_of_line(loop)
            self._loops[b] = Loop(b, **loop)

    def _init_pods_of_line(self, line):
        for pod in line["pods"]:
            pod["source"] = self._get_elt_of_loop(**pod["source"])
            pod["destination"] = self._get_elt_of_loop(**pod["destination"])
            _init_pod_of_line(line, pod)

    def _get_elt_of_loop(self, loop=None, element=None):
        """
        :param loop, element: numéro de la boucle et de l'élément s'y trouvant
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


def _init_pod_of_line(line, pod):
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
