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
from .Statistiques import *


class Network(Node):
    def __init__(self, env, id, bridges=None, loops=None, switches=None, roads=None, view_box=None, margin_min=None,
                 pod_size=None, max_speed=None, places_number=None, dynamic_routing=None, **kwargs):
        super().__init__(env, id, **kwargs)
        self._dynamic_routing = dynamic_routing or False
        self._last_routing_update = env.time
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
        #print("_init_graph_from_json done")
        self._init_parent_of_children()
        #print("_init_parent_of_children done")
        self._init_weights()
        #print("_init_weights done")
        # Initialisation de la table de routage de chaque aiguillage
        # C'est une liste de dictionnaires de la forme {"switch": s, "table": t}
        # où t contient les destinations pour lesquelles il faut tourner en s1
        self._routing_table = {}
        print("updating routing tables...")
        self._update_routing(init=True)  # création des tables de routage
        print("routing tables updated.")
        self.departure_arrival_printer = False  # mettre à vrai pour afficher des informations dans le terminal
        self._statistiques = Statistiques()
        # On cree les csv puis on ecrit les noms des colonnes
        self._statistiques.write_columns_names_for_all_stations(self.stations)
        # pour débugguer / profiler
        self.last_count = -1  # les 2 variables servent à afficher lorsqu'un pod est manquant dans le réseau
        self.last_pods = {}
        self._last_minute = int(self.env.time / 60)
        #self.last_sec = 1

    
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
    def statistiques(self):
        return self._statistiques

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
        for i_loop in range(len(self._loops)):
            self._loops[i_loop]["switches"] = []
            self._loops[i_loop]["roads"] = []
            steps = []
            sections = []
            elements = self._loops[i_loop]["elements"]
            roads = self._loops[i_loop]["roads"]
            if elements[0]["type"] not in ["switch_in", "switch_out"]:
                raise ValueError("Error: in network.py: loop %d must begin with a switch" % i_loop)
            for i_node in range(len(elements)):
                n = elements[i_node]
                section = self._loops[i_loop]["sections"][i_node]
                if n["type"] in ["switch_in", "switch_out"]:
                    id_bridge = n["id_bridge"]
                    
                    if n["type"] == "switch_in":
                        if "switch_in" in self._bridges[id_bridge]:
                            raise ValueError("Error: in network.py: bridge %d already has a switch in" % id_bridge)
                        self._bridges[id_bridge]["switch_in"] = {
                            "loop": i_loop,
                            "element": i_node
                        }
                    else:
                        if "switch_out" in self._bridges[id_bridge]:
                            print("error id =", id_bridge)
                            raise ValueError("Error: in network.py: bridge %d already has a switch out" % id_bridge)
                        self._bridges[id_bridge]["switch_out"] = {
                            "loop": i_loop,
                            "element": i_node
                        }
                    self._loops[i_loop]["switches"].append(n)
                    if i_node >= 1: # on saute le cas elements[0] (car c'est le 1er switch de la boucle)  # TODO : faire les étapes 1 à 4 plus proprement ? si possible ?
                        self._loops[i_loop]["roads"].append({
                            "steps": steps,
                            "sections": sections
                        })
                        steps = []
                        sections = []
                    sections.append(section)
                
                else:
                    # type: station, shed, sensor
                    n["element_of_loop"] = {
                        "loop": i_loop,
                        "element": i_node
                    }
                    steps.append(n)
                    sections.append(section)
                    
            # on ajoute la dernière road
            roads.append({
                "steps": steps,
                "sections": sections
            })
        
        loops_elems_count = [len(loop["elements"]) for loop in self._loops] # permettra de compter aussi les éléments des bridges rattachés aux boucles pour leur indexation
        for bridge in self._bridges: # pour les éléments des bridges, n["element_of_loop"]["loop"] est la boucle qui possède le switchOut vers ce bridge
            i_loop = bridge["switch_out"]["loop"]
            for n in bridge["elements"]:
                n["element_of_loop"] = {
                    "loop": i_loop,
                    "element": loops_elems_count[i_loop]
                }
                loops_elems_count[i_loop] += 1
        
        #  Etape 2 : Instanciation des routes
        for i_loop in range(len(self._loops)):
            roads = self._loops[i_loop]["roads"]
            for road in range(len(roads)):
                if "id" in roads[road]:
                    del roads[road]["id"]
                new_road = Road(env, len(self._roads), self._margin_min, self._pod_size, False, **roads[
                    road])  # Ici se fait la liaison des pistes (sections internes et étapes) : étape 42
                self._roads.append(new_road)
                roads[road] = new_road
        
        nb_roads = len(self._roads)  # nombre de routes du réseau qui sont internes aux boucles

        for b in range(len(self._bridges)):
            bridge = self._bridges[b]
            new_road = Road(env, nb_roads + b, self._margin_min, self._pod_size, True, **{
                "steps": bridge["elements"],
                "sections": bridge["sections"]
            })  # La liaison se fait au niveau de l'instanciation des switches (plus tard dans l'algo)
            self._roads.append(new_road)
            self._bridges[b]["roads"] = [new_road]  # On ajoute sa route au bridge
        
        #  Etape 3 : Instanciation des aiguillages, ajout de leurs capsules et liaison avec les routes
        for i_loop in range(len(self._loops)):
            first_switch = len(self._switches)
            for s in range(len(self._loops[i_loop]["switches"])):
                #  Capsules
                switch = self._loops[i_loop]["switches"][s]
                #  Routes et Id
                id_switch = len(self._switches)
                switch["previous"] = self._roads[
                    (id_switch - first_switch - 1) % len(self._loops[i_loop]["switches"]) + first_switch]  # loop_in
                switch["next"] = self._roads[id_switch]  # loop_out
                switch["beside"] = self._roads[nb_roads + switch["id_bridge"]]  # road_bridge
                if "id" in switch:
                    del switch["id"]
                if switch["type"] == "switch_in":
                    new_switch = SwitchIn(env, id_switch, self._margin_min, self._pod_size, max_speed, places_number,
                                          **switch)
                else:
                    new_switch = SwitchOut(env, id_switch, self._margin_min, self._pod_size, max_speed, **switch)
                self._switches.append(new_switch)
                self._loops[i_loop]["switches"][s] = new_switch
        
        #  Etape 4 : Instanciation des boucles et des ponts (sert pour la vue)
        for b in range(len(self._bridges)):
            bridge = self._bridges[b]
            self._init_pods_of_line(bridge)
            if "id" in bridge:
                del bridge["id"]
            self._bridges[b] = Bridge(b, **bridge)
        for i_loop in range(len(self._loops)):
            loop = self._loops[i_loop]
            self._init_pods_of_line(loop)
            if "id" in loop:
                del loop["id"]
            self._loops[i_loop] = Loop(i_loop, **loop)

        #print("NETWORK CREATED")

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
        if "pods" not in line:
            line["pods"] = []
        for pod in line["pods"]:
            pod["source"] = self._get_elt_of_loop(**pod["source"])
            pod["destination"] = self._get_elt_of_loop(**pod["destination"])
            _init_pod_of_line(line, pod)

    def _get_elt_of_loop(self, loop=None, element=None, **kwargs):
        """
        :param loop, element: numéro de la boucle et de l'élément s'y trouvant
        :return: l'objet retourné correspondant au numéro d'élément présent dans la boucle spécifiée
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

    def get_station_by_name(self, name):
        """
            return a station by its name
        """
        for station in self.stations:
            if station.name == name:
                return station
        return None

    def _init_weights(self):
        # Initialisation des poids des routes
        for road in self._roads:
            weight = 0
            for section in road.sections:
                weight += section.weight
            road.weight = weight

    def _is_destination(self, switch):
        """ Renvoie True si le switch fait partie d'une sérivation vers une station / shed. """
        # TODO : à déplacer dans les Switchs
        return len(switch.beside.sections) >= 2
    
    def _update_routing(self, init=False):
        """
        Envoie aux aiguillages sortant une nouvelle table de routage
        :return: void

        On construit la table de routage de chaque switch du réseau :
            la table de routage d'un switch indique si pour une destination donnée on doit tourner pour atteindre la desination
            la table contient donc une liste de destinations pour lesquelles il faut tourner
            les destinations restantes sont celles pour lesquelles il faut continuer dans la boucle
        
        """
        # initialisation d'une table globale
        for s in self._switches:
            if isinstance(s, SwitchOut):
                self._routing_table[s.name] = []
        # Switches menant aux stations/sheds
        for s in self._switches:
            if isinstance(s, SwitchOut) and s.is_destination():
                for step in s.beside.steps:
                    self._routing_table[s.name].append(step.name)
        # Remplissage pour les switchs entre 2 boucles différentes
        #i=1
        for s1 in self._switches:
            if isinstance(s1, SwitchOut) and not s1.is_destination():
                for s2 in self._switches:
                    if s1 != s2:
                        way = shortest_way(s1, s2)
                        if s1.switch_in in way:
                            # le plus court chemin menant à s2 passe par le bridge de s1,
                            # on ajoute donc à la table de s1 l'ensemble des éléments
                            # directement accessibles depuis s2.
                            # Attention : cela n'est vrai que parce qu'on sait que le
                            # bridge de s1 ne mène pas à la même boucle que s1.
                            if isinstance(s2, SwitchOut):
                                s2_steps = s2.next.steps[:] + s2.beside.steps[:]
                            else:
                                s2_steps = s2.next.steps[:]
                            for step in s2_steps:
                                self._routing_table[s1.name].append(step.name)
            #print("c %d / %d"%(i,len(self.switches)))
            #i+=1
        # Envoie des tables aux switchs
        if init:
            for switch in self._switches:
                if isinstance(switch, SwitchOut):
                    switch.routing_table = self._routing_table[switch.name]

    def maj_routing_tables(self):
        """pour mettre à jour les tables de routage"""
        self._update_routing(init=False)  # calcul des nouvelles tables
        for switch in self._switches:     # envoie des messages pour mettre à jour
            if isinstance(switch, SwitchOut):
                switch.write({
                    "author": self,
                    "type": "update_routing",
                    "table": self._routing_table[switch.name]
                })

    def find(self, step):
        for road in self._roads:
            for s in road.steps:
                if step["name"] == s.name:
                    return s
        raise ValueError("Step not in the network")
    
    @property
    def updatable(self):
        return True

    def update(self):

        #       Affichage des secondes de la simul si besoin de tester GET de l'API pr les durees de trajet
        #if ( round(self.env.time) % 60 == self.last_sec):
        #    print("last_sec = " + str(self.last_sec))       
        #    last_sec += 1
        #    if (self.last_sec == 60):
        #        self.last_sec = 0

        #print(self.env.time)
        
        current_minute = int(self.env.time / 60)
        if current_minute != self._last_minute:  # affichage et écriture en fichier toutes les minutes de simulations

            self._last_minute = current_minute
            print("\u001B[34m Temps de simulation: [" + str(datetime.timedelta(seconds=round(self.env.time))) +
                  "]\u001B[0m\n\t\t(network l.402)")
            if self.departure_arrival_printer:
                self.statistiques.print_stats()

            # ECRITURE STATS
            self.statistiques.write_stats_line(str(datetime.timedelta(seconds=round(self.env.time))))
            self.statistiques.write_stats_for_all_stations(str(datetime.timedelta(seconds=round(self.env.time))), self.stations)
            self.statistiques.write_stats_insertion(str(datetime.timedelta(seconds=round(self.env.time))), self.switches)
            self.statistiques.write_travel_time_global(str(datetime.timedelta(seconds=round(self.env.time))))
            # ligne calcul stats autres (voir txt perso)

        # si on veut tracer les pods du réseau pour débugguer :
        #self.last_count, self.last_pods = self.pods_du_reseau(self.last_count, self.last_pods)
        
        if self._dynamic_routing and (self.env.time > self._last_routing_update + 30*60 or self.env.time < self._last_routing_update):
            # Toutes les 30 secondes on met à jour les tables de routage si l'option est activée
            # ("self.env.time < self._last_routing_update" = passage de 23h59 à 00h00)
            #print("Updated routing tables...")
            self.maj_routing_tables()
            self._last_routing_update = self.env.time
            #print("Routing tables updated")
    
    def handle_message(self, message):
        if "docked" == message["type"]:
            # Une capsule stationne
            timestamp = message["timestamp"]
            if self.departure_arrival_printer:
                print("\u001B[35m[" + str(datetime.timedelta(seconds=round(timestamp))) +
                      "] Arrival\u001B[0m", message["pod"].destination, "\t\t(network l.396)", end='')
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
                shed.write({
                    "author": self,
                    "type": "refill",
                    "station": station
                })
        elif "empty" == message["type"]:
            # On demande à une station d'envoyer une capsule à un dépôt pour faire de la place
            #
            # TODO: ne pas choisir aléatoirement (vérifier que le shed a bien une place libre)
            #       + mettre un warning s'il n'y a plus de place dans les sheds
            #
            sheds = self.sheds
            if sheds:
                station = message["station"]
                shed = choice(sheds)
                station.write({
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
            self._statistiques.add_traveling_pod(message["pod"], timestamp, traveler, origin)
            if self.departure_arrival_printer:
                print("\u001B[36m[", str(datetime.timedelta(seconds=round(timestamp))),
                      "] Departure\u001B[0m ", origin, " -> ", destination,
                      "\n\t\t(network l.432)")
                print("\t\t\u001B[36m|\u001B[0m nom du pod:\t", message["pod"].name[:8])
                print("\t\t\u001B[36m|\u001B[0m waiting time:\t", str(round(waiting_time)) + " seconds")
                print("\t\t\u001B[36m|\u001B[0m traveler:\t\t", str(traveler), "\n")
            if traveler:
                # dans le cas d'un voyage (et non pas d'un appel pour combler l'espace dans une station),
                # on met à jour le compteur ici
                for station0 in self.stations:
                    if station0.name == destination:
                        station0.up_incoming_pods()
        else:
            raise ValueError("Invalid message")

    def pods_du_reseau(self, last_count, last_pods):
        """ permet d'afficher dans le terminal les pods du réseau, leur position et les compter quand un pod est manquant"""
        pods_du_reseau = {}
        nb_pods = 0
        for switch in self.switches:
            if len(switch.pods) != 0:
                pods_du_reseau[switch.name] = str(len(switch.pods))
            nb_pods += len(switch.pods)
        for road in self.roads:
            nb_pod_road = 0
            for pod in road.pods:
                if pod is not None:
                    nb_pod_road += 1
            if nb_pod_road != 0:
                if len(road.steps) != 0:
                    step_pods = " ["
                    for pod in road.steps[0].pods:
                        if pod is None:
                            step_pods += "None "
                        else:
                            step_pods += pod.name[:8] + " "
                    step_pods += "]"
                    pods_du_reseau[road.name] = str(nb_pod_road) + " (" + road.steps[0].name + step_pods + ")"
                else:
                    pods_du_reseau[road.name] = str(nb_pod_road)
            nb_pods += nb_pod_road
        if nb_pods != last_count and last_count != -1:
            print("\t\u001B[31mmodif nombre de pods:", last_count, "->", nb_pods, "\u001B[0m\t\t\t\t\t\t (network l.480)")
            for key in last_pods.keys():
                if key not in pods_du_reseau.keys():
                    print("\t|\t\t\u001B[31m", key, last_pods[key], ">>>", "--", "\u001B[0m")
            for key in pods_du_reseau.keys():
                if key not in last_pods.keys():
                    print("\t|\t\t\u001B[31m", key, " -- ", ">>>", pods_du_reseau[key], "\u001B[0m")
                elif last_pods[key] != pods_du_reseau[key]:
                    print("\t|\t\t\u001B[31m", key, last_pods[key], ">>>", pods_du_reseau[key], "\u001B[0m")
            print("\n")
        return nb_pods, pods_du_reseau


    def get_pod_of_user(self, user_id):
        """ Renvoie un objet pod qui est celui de l'user, si celui-ci est dans une capsule """

        moving_pods = self._statistiques.traveling_pods()
        for key in moving_pods:
            a_moving_pod = moving_pods[key]
            if (len(a_moving_pod) > 0):
                for a_traveler in a_moving_pod[0].travelers:
                    if (a_traveler.id == str(user_id)):
                        #print("User trouve !")
                        return a_moving_pod[0]
        
        return None         # Le voyageur n'est pas encore dans une capsule

    def get_total_sections_length(self):
        sections = [s for road in self._roads for s in road.sections]
        return sum([section.length for section in sections])
    
    def get_total_switches_length(self):
        for s in self._switches:
            if s.length == None:
                print("ERROR in network.py: switch not initialized.")
                return None
        return sum([switch.length for switch in self._switches])
    
    def get_station_with_name(self, name_of_station):
        for station in self.stations:
            if (station.name == name_of_station):
                return station
        print("station non trouvee dans le reseau")

    def pod_change_from_one_destination_to_another(self, former_dest, new_dest):
        former_dest_station = self.get_station_with_name(former_dest)
        new_dest_station = self.get_station_with_name(new_dest)
        former_dest_station.down_incoming_pods() # on decremente le nombre de pods qui vont arriver
        new_dest_station.up_incoming_pods()      # on incremente le nombre de pods qui vont arriver

####################    Fin classe


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

def shortest_way_tracks(start_track, destination_track):
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
        return shortest_way(next_switch_out(start_track), previous_switch_out(destination_track))

def shortest_way(start_switch, destination_switch):
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
                # ^ TODO : à adapter aux nouveaux bridges
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
    # TODO : à gérer lorsque les capsules se garent
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
    # liée à la congestion TCP si dans l'avenir c'est à remettre
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
