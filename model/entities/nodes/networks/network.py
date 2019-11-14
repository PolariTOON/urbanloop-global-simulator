"""
Cette classe gère un réseau entier, c'est le niveau meta-graph du réseau
les noeuds peuvent être des routes (partie interne d'une boucle) ou des ponts (pour relier les boucles)
"""
from math import inf
from random import choice

from ....lines.bridge import Bridge
from ....lines.loop import Loop
from ..node import Node
from .ways.road import Road
from .ways.switch_in import SwitchIn
from .ways.switch_out import SwitchOut
from .ways.tracks.station import Station
from .ways.tracks.section import Section


# TODO : Gérer les timers des capsules (temps de trajets)
# TODO : Gérer les stats
# TODO : drain des capsules superflues dans les gares


class Network(Node):
    def __init__(self, env, id, bridges=None, loops=None, switches=None, roads=None, view_box=None, margin_min=None,
                 pod_size=None, max_speed=None, places_number=None, dynamic_routing=None, **kwargs):
        super().__init__(env, id, **kwargs)
        self._dynamic_routing = dynamic_routing or False
        self._margin_min = margin_min or 2
        self._pod_size = pod_size or 2
        self._bridges = bridges or []
        self._loops = loops or []
        self._switches = switches or []
        self._roads = roads or []
        self._max_speed = max_speed or 30
        self._places_number = places_number or 5
        self._view_box = view_box or {}
        self._init_graph_from_json(env, max_speed, places_number)
        self._init_parent_of_children()
        self._init_weights()
        # Initialisation de la table de routage de chaque aiguillage
        # C'est une liste de ditcionnaire de la forme {"switch": s, "table": t}
        # où t contient les destinations pour lesquelles il faut tourner en s1
        self._routing_table = []
        for s1 in self._switches:
            if isinstance(s1, SwitchOut):
                table = []
                for s2 in self._switches:
                    if isinstance(s2, SwitchOut):
                        way = shorter_way(s1, s2)
                        for index in range(len(way) - 1):
                            s = way[index]
                            if s.next.next in way:
                                road = s.next
                            else:
                                road = s.beside
                            for step in road.steps:
                                table.append(step)
                self._routing_table.append({"switch": s1, "table": table})
        # Initialisation des tables de routage des aiguillages
        for switch in self._switches:
            if isinstance(switch, SwitchOut):
                switch.routing_table = self._get_switch_table(switch)

    @property
    def name(self):
        return super().name or "Network %d" % self.id

    @property
    def pods(self):
        pods = []
        for road in self._roads:
            for pod in road.pods:
                pods.append(pod)
        return pods

    @property
    def bridges(self):
        return self._bridges

    @property
    def loops(self):
        return self._loops

    @property
    def switches(self):
        return self._switches

    @property
    def roads(self):
        return self._roads

    @property
    def sensors(self):
        return [sensor for road in self._roads for sensor in road.sensors]

    @property
    def sheds(self):
        return [shed for road in self._roads for shed in road.sheds]

    @property
    def stations(self):
        return [station for road in self._roads for station in road.stations]

    @property
    def stations_names(self):
        return [station.name for road in self._roads for station in road.stations]

    @property
    def margin_min(self):
        return self._margin_min

    @property
    def max_speed(self):
        return self._max_speed

    @property
    def pod_size(self):
        return self._pod_size

    @property
    def places_number(self):
        return self._places_number

    @property
    def dynamic_routing(self):
        return self._dynamic_routing

    @property
    def view_box(self):
        if self._view_box:
            return self._view_box
        min_x = inf
        max_x = 0
        min_y = inf
        max_y = 0
        for loop in self._loops:
            if loop.x_min < min_x:
                min_x = loop.x_min
            if loop.x_max > max_x:
                max_x = loop.x_max
            if loop.y_min < min_y:
                min_y = loop.y_min
            if loop.y_max > max_y:
                max_y = loop.y_max
        width = max_x - min_x
        height = max_y - min_y
        return {"x": 0, "y": 0, "width": width, "height": height}

    def serialize(self):
        bridges = [bridge.serialize() for bridge in self._bridges]
        loops = [loop.serialize() for loop in self._loops]
        dict = super().serialize()
        dict.update({
            "loops": loops,
            "bridges": bridges,
            "view_box": self.view_box,
            "margin_min": self.margin_min,
            "max_speed": self.max_speed,
            "pod_size": self.pod_size,
            "places_number": self.places_number,
            "dynamic_routing": self.dynamic_routing
        })
        return dict

    def _init_graph_from_json(self, env, max_speed, places_number):
        """
        Création du model à partir du dictionnaire obtenu à partir du fichier json
        :return: (void) Le réseau est construit
        """
        #  Etape 1 : Récupérer les infos du json sous forme pratique
        for bridge in self._bridges:
            if "switch_in" in bridge:
                del bridge["switch_in"]
            if "switch_out" in bridge:
                del bridge["switch_out"]
        for b in range(len(self._loops)):
            self._loops[b]["switches"] = []
            self._loops[b]["roads"] = []
            steps = []
            sections = []
            elements = self._loops[b]["elements"]
            roads = self._loops[b]["roads"]
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
                    self._loops[b]["roads"].append({
                        "steps": steps,
                        "sections": sections
                    })
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
            roads.append({
                "steps": steps,
                "sections": sections
            })
        #  Etape 2 : Instanciation des routes
        for b in range(len(self._loops)):
            roads = self._loops[b]["roads"]
            for road in range(1, len(roads)):
                if "id" in roads[road]:
                    del roads[road]["id"]
                new_road = Road(env, len(self._roads), self._margin_min, self._pod_size, False, **roads[
                    road])  # Ici se fait la liaison des pistes (sections internes et étapes) : étape 42
                self._roads.append(new_road)
                #  Comme le premier elt est une liste vide on remet les elts en remplaçant celle-ci
                roads[road - 1] = new_road
            roads.pop()
        l = len(self._roads)  # nombre de routes du réseau internes aux boucles
        for p in range(len(self._bridges)):
            steps = []
            sections = [self._bridges[p]["section"]]
            new_road = Road(env, l + p, self._margin_min, self._pod_size, True, **{
                "steps": steps,
                "sections": sections
            })  # La liaison se fait au niveau de l'instanciation des switches (plus tard dans l'algo)
            self._roads.append(new_road)
            self._bridges[p]["roads"] = [new_road]  # On ajoute sa route au bridge
        #  Etape 3 : Instanciation des aiguillages, ajout de leurs capsules et liaison avec les routes
        for b in range(len(self._loops)):
            first_switch = len(self._switches)
            for s in range(len(self._loops[b]["switches"])):
                #  Capsules
                switch = self._loops[b]["switches"][s]
                pods = switch["pods"]
                for pod_branch_key in pods:
                    pod_branch = pods[pod_branch_key]
                    for pod_index in range(len(pod_branch)):
                        pod = pod_branch[pod_index]
                        pod["source"] = self._get_elt_of_loop(**pod["source"])
                        pod["destination"] = self._get_elt_of_loop(**pod["destination"])
                #  Routes et Id
                id_switch = len(self._switches)
                switch["previous"] = self._roads[
                    (id_switch - first_switch - 1) % len(self._loops[b]["switches"]) + first_switch]  # loop_in
                switch["next"] = self._roads[id_switch]  # loop_out
                switch["beside"] = self._roads[l + switch["id_bridge"]]  # road_bridge
                if "id" in switch:
                    del switch["id"]
                if switch["type"] == "switch_in":
                    new_switch = SwitchIn(env, id_switch, self._margin_min, self._pod_size, max_speed, places_number,
                                          **switch)
                else:
                    new_switch = SwitchOut(env, id_switch, self._margin_min, self._pod_size, max_speed, **switch)
                self._switches.append(new_switch)
                self._loops[b]["switches"][s] = new_switch
        #  Etape 4 : Instanciation des boucles et des ponts (sert pour la vue)
        for p in range(len(self._bridges)):
            bridge = self._bridges[p]
            switch_out = self._get_elt_of_loop(**bridge["switch_out"])
            switch_in = self._get_elt_of_loop(**bridge["switch_in"])
            bridge["switches"] = [switch_out, switch_in]
            self._init_pods_of_line(bridge)
            if "id" in bridge:
                del bridge["id"]
            self._bridges[p] = Bridge(p, **bridge)
        for b in range(len(self._loops)):
            loop = self._loops[b]
            self._init_pods_of_line(loop)
        for b in range(len(self._loops)):
            loop = self._loops[b]
            if "id" in loop:
                del loop["id"]
            self._loops[b] = Loop(b, **loop)

    def _init_station(self):
    	#mise à jour de l'initialisation d'une station, afin de modéliser les voies d'entrée et de sortie à une station.
    	#on y rajoute un switch in et un switch out sur la boucle qui contient la gare afin d'y entrer et d'y sortir
    	#on crée une nouvelle boucle pour la station qui va contenir un switch in pour rentrer dans la station, un switch out pour en sortir et la station entre les 2 ainsi que 3 sections pour relier ces éléments
    	#cela implique aussi de rajouter les 2 bridges nécessaires pour relier les switchs
    	id_loop = len(self._loops)
    	new_loop = Loop(id_loop)
    	
    	id_road = len(self._roads)
    	new_road1 = Road(env, id_road, self._margin_min, self._pod_size, False)
    	new_road2 = Road(env, id_road + 1, self._margin_min, self._pod_size, False)

    	id_station = len(self._stations)
    	new_station = Station(env, id_station, name="test")

    	id_switch = len(self._switches)
    	new_switch_in = SwitchIn(env, id_switch, self._margin_min, self._pod_size, max_speed, places_number)
    	new_switch_out = SwitchOut(env, id_switch + 1, self._margin_min, self._pod_size, max_speed)

    	new_section0 = Section(env, 0, margin_min, pod_size, is_bridge)
    	new_section1 = Section(env, 1, margin_min, pod_size, is_bridge)
    	new_section2 = Section(env, 2, margin_min, pod_size, is_bridge)

    def _init_parent_of_children(self):
        """
        Initialise le parent des routes et aiguillages comme étant le réseau
        :return: void
        """
        for switch in self._switches:
            switch.parent = self
        for road in self._roads:
            road.parent = self
            road.init_parent_of_children()

    def _init_pods_of_line(self, line):
        for pod in line["pods"]:
            pod["source"] = self._get_elt_of_loop(**pod["source"])
            pod["destination"] = self._get_elt_of_loop(**pod["destination"])
            _init_pod_of_line(line, pod)

    def _get_elt_of_loop(self, loop=None, element=None, **kwargs):
        """
        :param loop, element: numéro de la boucle et de l'élément s'y trouvant
        :return: l'objet instancié correspondant au numéro d'élément présent dans la boucle spécifiée
        """
        #  Initialisation des variables
        if loop < 0 or loop > len(self._loops):
            raise ValueError("Loop's index out of range")
        loop = self._loops[loop]
        roads = loop["roads"]
        switches = loop["switches"]
        if element < 0:
            raise ValueError("Element's index out of range")
        elt = 0
        #  Recherche du noeud
        for r in range(len(roads)):
            if elt == element:  # L'element est un switch
                return switches[r]
            elt += 1
            steps = roads[r].steps
            for s in range(len(steps)):
                if elt == element:  # L'element est une etape
                    return steps[s]
                elt += 1
        raise ValueError("Element's index out of range")

    def _init_weights(self):
        # Initialisation des poids des routes
        for road in self._roads:
            weight = 0
            for section in road.sections:
                weight += section.weight
            road.weight = weight

    def _update_routing(self):
        """
        Envoie aux aiguillages sortant une nouvelle table de routage
        :return: void
        """
        # Maj des tables
        for s1 in self._switches:
            if isinstance(s1, SwitchOut):
                table = []
                for s2 in self._switches:
                    if isinstance(s2, SwitchOut):
                        way = shorter_way(s1, s2)
                        for index in range(len(way) - 1):
                            s = way[index]
                            if s.next.next in way:
                                road = s.next
                            else:
                                road = s.beside
                            for step in road.steps:
                                table.append(step)
                self._routing_table.append({"switch": s1, "table": table})
        # Envoie des tables
        for switch in self._switches:
            if isinstance(switch, SwitchOut):
                yield from switch.write({
                    "author": self,
                    "type": "update_routing",
                    "table": self._get_switch_table(switch)
                })

    def _get_switch_table(self, switch):
        for dico in self._routing_table:
            if dico["switch"] == switch:
                return dico["table"]
        raise ValueError("Switch not in the routing table")

    def find(self, step):
        for road in self._roads:
            for s in road.steps:
                if step["name"] == s.name:
                    return s
        raise ValueError("Step not in the network")

    def update(self):
        """
        Gestion du processus du réseau à chaque boucle d'événement simpy
        :return: void
        """
        while True:
            #print("-------------------------------------------------------------")
            #print("     Tick n°", int(self.env.now), " | Réseau :", self.name, "     ")
            #print("-------------------------------------------------------------")
            if self._dynamic_routing and int(int(self.env.now) % (30 / self.env.tick)) == 0:  # TODO: utilise self.env.time plutôt que self.env.tick
                # Toutes les 30 secondes on met à jour les tables de routage si l'option est activée
                yield from self._update_routing()
            while True:
                message = yield from self.read()
                if message is None:
                    break
                elif "docked" == message["type"]:
                    # Une capsule stationne
                    pass
                elif "refill" == message["type"]:
                    # On demande à un dépôt d'envoyer une capsule à la station qui le demande
                    # TODO:  ne pas choisir aléatoirement
                    sheds = self.sheds
                    if sheds:
                        station = message["station"]
                        shed = choice(sheds)
                        yield from shed.write({
                            "author": self,
                            "type": "refill",
                            "station": station
                        })
                elif "empty" == message["type"]:
                    # On demande à un dépôt d'envoyer une capsule à la station qui le demande
                    # TODO:  ne pas choisir aléatoirement
                    sheds = self.sheds
                    if sheds:
                        station = message["station"]
                        shed = choice(sheds)
                        yield from station.write({
                            "author": self,
                            "type": "empty",
                            "shed": shed
                        })
                else:
                    raise ValueError("Invalid message")


def _init_pod_of_line(line, pod):
    position = pod["position"]
    if position < 0:
        raise ValueError("Element's position out of range")
    for road in line["roads"]:
        for section in road.sections:
            length = section.length
            if position < length:
                pod["position"] = position
                section.insert_pod(**pod)
                return
            position -= length
    raise ValueError("Element's position out of range")


def shorter_way_tracks(start_track, destination_track):
    """
    Lance le calcul du plus court chemin si nécéssaire (i.e si les pistes sont sur des routes différentes)
    :param start_track: piste de départ
    :param destination_track: piste d'arrivée
    :return: liste d'aiguillages représentant le plus court chemin pour aller de star_switch à destination_switch
    Si elle est vide alors les pistes sont sur la même route
    """
    if previous_switch_out(start_track) == previous_switch_out(destination_track):
        return []
    else:
        return shorter_way(next_switch_out(start_track), previous_switch_out(destination_track))


def shorter_way(start_switch, destination_switch):
    """
    Calcul du plus court chemin entre deux aiguillages avec l'algorithme de Dijkstra
    :param start_switch: aiguillage de départ
    :param destination_switch: aiguillage d'arrivé
    :return: liste d'aiguillages représentant le plus court chemin pour aller de star_switch à destination_switch
    """
    way = [(0, start_switch)]
    best_weight = {start_switch: 0}
    previouses = {}
    visited = set()
    while True:
        if way:
            entry = way.pop()
        else:
            break
        weight, switch = entry
        if switch not in visited:
            visited.add(switch)
            if switch == destination_switch:
                break
            # On a toujours le next comme successeur
            new_weight = weight + switch.next.weight
            min_weight = best_weight.get(switch.next.next)
            if min_weight is None or new_weight < min_weight:
                best_weight[switch.next.next] = new_weight
                previouses[switch.next.next] = switch
                way.append((new_weight, switch.next.next))
            if isinstance(switch, SwitchOut):  # Pour un out on a aussi le beside comme successeur
                new_weight = weight + switch.beside.weight
                min_weight = best_weight.get(switch.beside.next)
                if min_weight is None or new_weight < min_weight:
                    best_weight[switch.beside.next] = new_weight
                    previouses[switch.beside.next] = switch
                    way.append((new_weight, switch.beside.next))
    weight = best_weight.get(destination_switch)
    way = []
    if weight is not None:
        switch = destination_switch
        while switch is not None:
            way = [switch] + way
            switch = previouses.get(switch)
    return way


def next_switch_out(track):
    """
    :param track: piste dont on veut connaître l'aiguillage sortant suivant le plus proche
    :return: L'aiguillage sortant suivant le plus proche du track en entrée
    """
    current = track
    while not isinstance(current, SwitchOut):
        current = current.next
    return current


def previous_switch_out(track):
    """
    :param track: piste dont on veut connaître l'aiguillage sortant précédent le plus proche
    :return: L'aiguillage sortant précédent le plus proche du track en entrée
    """
    current = track
    while not isinstance(current, SwitchOut):
        current = current.previous
    return current


def update_weight(switch1, switch2, travel_time):
    """
    Met à jour le poids de la route reliant switch1 à switch2 qu'une capsule vient de parcourir
    S'ils ne sont pas reliés alors ne fait rien
    :param travel_time: temps mis par la capsule pour parcourir la route
    :param switch1: switch précédent la route empruntée par la capsule
    :param switch2: switch suivant la route empruntée par la capsule
    :return: boolean indiquant si il y a congestion
    """
    # TODO : à gérer lorsque les capsules se gare
    if switch1.next.next == switch2:
        road = switch1.next
    elif switch1.beside.next == switch2:
        road = switch1.beside
    else:
        return False
    road.weight = 0.875 * road.weight + 0.125 * travel_time
    return road.weight > 3 * road.expected_weight


def no_more_congestion(previous_switch, current_switch):
    """
    :param previous_switch: aiguillage précédent
    :param current_switch: aiguillage actuel
    :return: boolean étant true s'il n'y a plus de congestion sur la route entre les deux aiguillages et false sinon
    """
    # TODO : liée à la congestion TCP si dans l'avenir c'est à remettre
    if previous_switch.next.next == current_switch:
        road = previous_switch.next
    elif previous_switch.beside.next == current_switch:
        road = previous_switch.beside
    else:
        return True
    return road.weight < 2 * road.expected_weight


def disable_road(previous_switch, current_switch):
    """
    Rend impossible le passage par une route, ie met le poids de celle-ci à l'infini
    :param previous_switch: aiguillage de début de route
    :param current_switch: aiguillage de fin de route
    """
    # TODO : peut etre utile pour une futur coupure de voie
    if previous_switch.next.next == current_switch:
        road = previous_switch.next
    elif previous_switch.beside.next == current_switch:
        road = previous_switch.beside
    else:
        return
    road.weight = inf


def get_time_max(previous_switch, current_switch):
    """
    Retourne le temps à partir duquel on considère une route comme coupée. On prend comme limite
    10 * le temps de parcours en conditions normales
    :param previous_switch: aiguillage précédent la route
    :param current_switch: aiguillage suivant la route
    :return: temps à partir duquel on considère une route comme coupée
    """
    # TODO : peut etre utile pour une futur coupure de voie
    if previous_switch.next.next == current_switch:
        road = previous_switch.next
    elif previous_switch.beside.next == current_switch:
        road = previous_switch.beside
    else:
        return -1
    return 10 * road.expected_weight
