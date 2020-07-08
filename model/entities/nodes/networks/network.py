"""
Cette classe gère un réseau entier, c'est le niveau meta-graph du réseau
les noeuds peuvent être des routes (partie interne d'une boucle) ou des ponts (pour relier les boucles)
"""
from math import inf
from random import choice
import datetime

from ....lines.bridge import Bridge
from ....lines.loop import Loop
from ..node import Node
from .ways.road import Road
from .ways.switch_in import SwitchIn
from .ways.switch_out import SwitchOut
from .ways.tracks.station import Station
from .ways.tracks.section import Section
from .Statistiques import *

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
        self._statistiques = Statistiques()
        # Initialisation de la table de routage de chaque aiguillage
        # C'est une liste de dictionnaires de la forme {"switch": s, "table": t}
        # où t contient les destinations pour lesquelles il faut tourner en s1
        self._routing_table0 = {}
        self._update_routing(init=True)  # création des tables de routage

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
            "dynamic_routing": self.dynamic_routing,
            "stats": self._statistiques.serialize()
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
            # pod["source"] = self._get_elt_of_loop(**pod["source"]) # faux on ne change pas les sources et destination d'une capsule
            # pod["destination"] = self._get_elt_of_loop(**pod["destination"])
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

    def _update_routing(self, init=False):
        """
        Envoie aux aiguillages sortant une nouvelle table de routage
        :return: void
        """
        """
        On construit la table de routage de chaque switch du réseau:
            la table de routage d'un switch indique si pour une destination donnée on doit tourner pour atteindre la desination
            la table contient donc une liste de destinations pour lesquelles il faut tourner
            les destinations restantes sont celles pour lesquelles il faut continuer dans la boucle

        Pour construire les tables:
            On calcule les plus courts chemins entre les switchs du réseau
                Pour chaque dépot/station à l'arrivée d'un chemin (destination),
                Pour chaque switch de ce chemin, s'il faut tourner pour atteindre la destination,
                 on ajoute la destination à la table de ce switch
        """
        for s0 in self._switches:   # initialisation d'une table globale
            if isinstance(s0, SwitchOut):
                self._routing_table0[s0.name] = []
        # Remplissage
        for s1 in self._switches:
            if isinstance(s1, SwitchIn):
                for s2 in self._switches:
                    if isinstance(s2, SwitchIn):
                        way = shorter_way(s1, s2)   # on calcul le plus court chemin entre nos 2 switchs
                        last_switch = way[-1]
                        steps = last_switch.next.steps
                        if steps != []:
                            for index in range(len(way)-1):
                                s = way[index]
                                if s.next.next != way[(index+1) % len(way)]:
                                    if steps[0].name not in self._routing_table0[s.name]:
                                        self._routing_table0[s.name].append(steps[0].name)
        if init:  # Envoie des tables
            # Initialisation des tables de routage des aiguillages
            for switch in self._switches:
                if isinstance(switch, SwitchOut):
                    switch.routing_table = self._routing_table0[switch.name]

    def maj_routing_tables(self):
        """pour mettre à jour les tables de routage"""
        self._update_routing(init=False)  # calcul des nouvelles tables
        for switch in self._switches:     # envoie des messages pour mettre à jour
            if isinstance(switch, SwitchOut):
                yield from switch.write({
                    "author": self,
                    "type": "update_routing",
                    "table": self._routing_table0[switch.name]
                })

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
                yield from self.maj_routing_tables()
            while True:
                message = yield from self.read()
                if message is None:
                    break
                elif "docked" == message["type"]:
                    # Une capsule stationne
                    timestamp = message["timestamp"]
                    print("\u001B[35m[" + str(datetime.timedelta(seconds=round(timestamp))) +
                          "] Arrival\u001B[0m", message["pod"].destination, "\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t(network l.396)", end='')
                    print("\n\t\t\u001B[35m|\u001B[0m nom du pod:", message["pod"].name[:8], "\n")
                    self._statistiques.remove_traveling_pod(message["pod"], timestamp)
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
                    # On demande à une station d'envoyer une capsule à un dépôt pour faire de la place
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
                elif "departure" == message["type"]:
                    timestamp = message["timestamp"]
                    origin = message["origin"]
                    destination = message["destination"]
                    waiting_time = message["waiting_time"]
                    traveler = message["traveler"]
                    self._statistiques.add_waiting_time(timestamp, waiting_time)
                    print("\u001B[36m[" + str(datetime.timedelta(seconds=round(timestamp)))
                          + "] Departure\u001B[0m ", origin, " -> ", destination,
                          "\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t(network l.432)")
                    print("\t\t\u001B[36m|\u001B[0m nom du pod:\t", message["pod"].name[:8])
                    print("\t\t\u001B[36m|\u001B[0m waiting time:\t", str(round(waiting_time)) + " seconds")
                    print("\t\t\u001B[36m|\u001B[0m traveler:\t\t", str(traveler), "\n")
                    self._statistiques.add_traveling_pod(message["pod"], timestamp, traveler)
                    if traveler:
                        # dans le cas d'un voyage,
                        # ce n'est pas une capsule appelée par la station pour combler l'espace
                        # on met à jour le compteur ici
                        for station0 in self.stations:
                            if station0.name == destination:
                                station0.up_incoming_pods()
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
    best_weight = {}                    # set des chemins le plus court (mis à jour pendant l'algorithme)
    best_weight[start_switch] = 0       # le coût d'atteinte du premier noeud est 0
    previouses = {}                     # switchs précédents (pour remonter l'algorithme -> indique l'origine des switchs')
    visited = set()                     # init ensemble des éléments visités (set est une "liste sans doublon")
    current_switch = start_switch
    while True:
        if current_switch in best_weight.keys():
            weight = best_weight[current_switch]
        else:
            break
        switch = current_switch
        if switch not in visited:
            visited.add(switch)
            if switch == destination_switch:
                break
            new_weight = weight + switch.next.weight            # pour établir le poids du chemin actuel
            if switch.next.next not in best_weight.keys() or new_weight < best_weight[switch.next.next]:  # si aucun chemin n'existe ou que celui-ci est plus court
                best_weight[switch.next.next] = new_weight  # on change la valeur dans la table
                previouses[switch.next.next] = switch       # on note que le prédécessur du switch.next.next est le switch actuel
            if isinstance(switch, SwitchOut):  # Pour un out on a aussi le beside comme successeur
                new_weight = weight + switch.beside.weight
                if switch.beside.next not in best_weight.keys() or new_weight < best_weight[switch.beside.next]:
                    best_weight[switch.beside.next] = new_weight
                    previouses[switch.beside.next] = switch

            # sélection du prochain noeud pour poursuivre l'algorithme (noeud le moins loin non-visité)
            weight0 = float("inf")
            for switch0 in best_weight.keys():
                if switch0 not in visited and best_weight[switch0] < weight0:
                    weight0 = best_weight[switch0]
                    current_switch = switch0
    weight = best_weight[destination_switch]  # taille minimale du chemin
    way = []                                  # construction du chemin
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
