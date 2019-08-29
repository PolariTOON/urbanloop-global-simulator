"""
Cette classe gère un réseau entier, c'est le niveau meta-graph du réseau
les noeuds peuvent être des routes (partie interne d'une boucle) ou des ponts (pour relier les boucles)
"""
from math import inf
from random import choice, uniform, random

from stats.stats_recorder import StatsRecorder

from ....lines.bridge import Bridge
from ....lines.loop import Loop
from ..node import Node
from .ways.tracks.station import station_types
from .ways.route import Route
from .ways.switch_in import SwitchIn
from .ways.switch_out import SwitchOut


class Network(Node):
    def __init__(self, env, id, bridges=None, loops=None, switches=None, routes=None, view_box=None, margin_min=None, pod_size=None, max_speed=None, places_number=None, dynamic_routing=None, **kwargs):
        super().__init__(env, id, **kwargs)
        self._dynamic_routing = dynamic_routing or False
        self._margin_min = margin_min or 2
        self._pod_size = pod_size or 2
        self._bridges = bridges or []
        self._loops = loops or []
        self._switches = switches or []
        self._routes = routes or []
        self._view_box = view_box or {}
        self._init_graph_from_json(env, max_speed, places_number)
        self._init_parent_of_children()
        self._recorder = StatsRecorder(0)  # TODO : Gérer les stats
        self._timers = [-1] * len(self.pods)  # TODO : Gérer les timers des capsules (temps de trajets)
        self._tab_depart = []  # TODO : Gérer les stats
        self._tab_temps = []  # TODO : Gérer les stats
        self._tab_depart_voy = []  # TODO : Gérer les stats
        self._tab_temps_voy = []  # TODO : Gérer les stats
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
                                route = s.next
                            else:
                                route = s.beside
                            for step in route.steps:
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
        for route in self._routes:
            for pod in route.pods:
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
    def routes(self):
        return self._routes

    @property
    def sensors(self):
        return [sensor for route in self._routes for sensor in route.sensors]

    @property
    def sheds(self):
        return [shed for route in self._routes for shed in route.sheds]

    @property
    def stations(self):
        return [station for route in self._routes for station in route.stations]

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

    def get_random_free_shed(self):
        free_sheds = [shed for route in self._routes for shed in route.sheds if len(shed.pods) < shed.capacity]
        return choice(free_sheds)

    def get_random_station_from_type(self, station_type, departure_station=None):
        """
        If departure_station is None, it means that you are looking for
        a random departure_station. Otherwise, it means that you are
        looking for a destination_station and this station can't be the
        same as the departure_station
        """
        stations = [station for route in self._routes for station in route.stations if
                    station.type == station_type and (departure_station is None or station != departure_station)]
        return choice(stations)

    def serialize(self):
        bridges = [bridge.serialize() for bridge in self._bridges]
        loops = [loop.serialize() for loop in self._loops]
        dict = super().serialize()
        dict.update({
            "loops": loops,
            "bridges": bridges,
            "view_box": self.view_box
        })
        return dict

    def _init_graph_from_json(self, env, max_speed, places_number):
        """
        Création du model à partir du dictionnaire obtenu à partir du fichier json
        :return: (void) Le réseau est construit
        """
        #  Etape 1 : Récupérer les infos du json sous forme pratique
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
                    self._loops[b]["routes"].append({
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
            routes.append({
                "steps": steps,
                "sections": sections
            })
        #  Etape 2 : Instanciation des routes
        for b in range(len(self._loops)):
            routes = self._loops[b]["routes"]
            for route in range(1, len(routes)):
                new_route = Route(env, len(self._routes), self._margin_min, self._pod_size, False, **routes[
                    route])  # Ici se fait la liaison des pistes (sections internes et étapes) : étape 42
                self._routes.append(new_route)
                #  Comme le premier elt est une liste vide on remet les elts en remplaçant celle-ci
                routes[route - 1] = new_route
            routes.pop()
        l = len(self._routes)  # nombre de routes du réseau internes aux boucles
        for p in range(len(self._bridges)):
            steps = []
            sections = [self._bridges[p]["section"]]
            new_route = Route(env, l + p, self._margin_min, self._pod_size, True, **{
                "steps": steps,
                "sections": sections
            })  # La liaison se fait au niveau de l'instanciation des switches (plus tard dans l'algo)
            self._routes.append(new_route)
            self._bridges[p]["routes"] = [new_route]  # On ajoute sa route au bridge
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
                switch["previous"] = self._routes[
                    (id_switch - first_switch - 1) % len(self._loops[b]["switches"]) + first_switch]  # loop_in
                switch["next"] = self._routes[id_switch]  # loop_out
                switch["beside"] = self._routes[l + switch["id_bridge"]]  # route_bridge
                if switch["type"] == "switch_in":
                    new_switch = SwitchIn(env, id_switch, self._margin_min, self._pod_size, max_speed, places_number, **switch)
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
            self._bridges[p] = Bridge(p, **bridge)
        for b in range(len(self._loops)):
            loop = self._loops[b]
            self._init_pods_of_line(loop)
        for b in range(len(self._loops)):
            loop = self._loops[b]
            self._loops[b] = Loop(b, **loop)

    def _init_parent_of_children(self):
        """
        Initialise le parent des routes et aiguillages comme étant le réseau
        :return: void
        """
        for switch in self._switches:
            switch.parent = self
        for route in self._routes:
            route.parent = self
            route.init_parent_of_children()

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

    # TODO : gérer les stats
    def travel_stats(self):
        """
        On obtient dans staats le temps moyen de trajet des capsules et dans staatsvoy le temps moyen
        d'attentes des voyageurs
        """
        latest_stats_file = open("out/staats.txt", "a+")
        buffer = str(self.temps_moy()) + ","
        latest_stats_file.write(buffer)
        latest_stats_file.close()
        latest_stats_file = open("out/staatsvoy.txt", "a+")
        buffer = str(self.temps_moy_voy()) + ","
        latest_stats_file.write(buffer)
        latest_stats_file.close()

    # TODO : gérer les stats
    def temps_moy_stat(self, id, temps):
        test = True
        for i in self._tab_depart:
            if i[0] == id:
                test = False
                self._tab_temps.append(temps - i[1])
                i[0] = -1
        if test:
            self._tab_depart.append([id, temps])

    # TODO : gérer les stats
    def temps_moy_voy_stat(self, id, temps):
        test = True
        for i in self._tab_depart_voy:
            if i[0] == id:
                test = False
                self._tab_temps_voy.append(temps - i[1])
                i[0] = -1
        if test:
            self._tab_depart_voy.append([id, temps])

    # TODO : gérer les stats
    def temps_moy_voy(self):
        moy = 0
        j = 0
        for i in self._tab_temps_voy:
            j += 1
            moy += i
        if j == 0:
            return 0
        else:
            return moy / j

    # TODO : gérer les stats
    def temps_moy(self):
        moy = 0
        j = 0
        for i in self._tab_temps:
            j += 1
            moy += i
        if j == 0:
            return 0
        else:
            return moy / j

    # TODO : gérer les stats
    def extract(self, simulated_time):
        self._recorder.stop_listen(simulated_time)
        self._recorder.extract()

    def select_random_station(self, second, probability, departure_station=None):
        """
        If departure_station is None, it means that you are looking for
        a random departure_station. Otherwise, it means that you are
        looking for a destination_station.
        """
        is_arrival = departure_station is not None
        city_prob = probability.station_probability(station_types["city"], second, is_arrival=is_arrival)
        residential_prob = probability.station_probability(station_types["residential"], second,
                                                           is_arrival=is_arrival) + city_prob
        activity_prob = probability.station_probability(station_types["activity"], second,
                                                        is_arrival=is_arrival) + residential_prob
        prob = uniform(0, 1)

        if prob < city_prob:
            return self.get_random_station_from_type(station_types["city"], departure_station=departure_station)
        elif prob < residential_prob:
            return self.get_random_station_from_type(station_types["residential"], departure_station=departure_station)
        elif prob < activity_prob:
            return self.get_random_station_from_type(station_types["activity"], departure_station=departure_station)
        else:
            return self.get_random_station_from_type(station_types["city"], departure_station=departure_station)

    def _init_weights(self):
        # Initialisation des poids des routes
        for route in self._routes:
            weight = 0
            for section in route.sections:
                weight += section.weight
            route.weight = weight

    def ascend_travelers(self, _env, second, probability, config, frequency):
        """
        Fait monter des voyageurs dans les capsules des stations, fonction appelée à chaque tick
        :param _env: environement simpy de la simulation
        :param second: temps simulé (= correspondant au temps réel) en seconde
        :param probability: instance de la classe probability propre à la simulation
        :param config: dictionnaire contenant la configuration du réseau
        :param frequency: nombre de ticks par seconde
        :return: déclenche des événements de monté de voyageurs dans les capsules des stations
        """
        trip_limit = int(config["TRAVELER"]["trip_limit"])
        for station in self.stations:
            if station.travelers and station.pods and (trip_limit > 0 or trip_limit == -1):
                if trip_limit != -1:
                    trip_limit -= 1
                if station.pods:
                    return

                station.travelers.pop(0)
                pod = station.pods[-1]
                destination = self.select_random_station(second, probability, departure_station=station)
                pod.add_traveler(destination)
                # sim_loop.recorder.add_waiting_time_traveler(traveler.get_waiting_seconds(), traveler) TODO : STATS A GENERER
                yield _env.process(
                    ascent_event(station, pod, _env, config["TRAVELER"]["ascent_descent_duration"], frequency))

    def generate_travelers(self, traveler_limit, traveler_number, second, probability):
        """
        Génère un certain nombre de voyageurs répartis aléatoirement dans les stations
        :param traveler_limit: nombre maximum de voyageurs dans le réseau
        :param traveler_number: nombre de voyageurs à générer
        :param second: temps simulé (= correspondant au temps réel) en seconde
        :param probability: instance de la classe probability propre à la simulation
        :return: (void) génère un certain nombre de voyageurs
        """
        if not (traveler_limit > 0 or traveler_limit == -1):
            return
        for a_traveler in range(traveler_number):
            if traveler_limit != -1:
                traveler_limit -= 1
            source = self.select_random_station(second, probability)
            source.travelers.append(0)
            # self.temps_moy_voy_stat(self.id, sim_loop.get_simulated_time())  # TODO : STATS A GERER

    def drain_pod_station(self, station):
        """
        Libère une capsule vide de la station si elle est à 3/4 pleine
        La capsule est redirigée vers un dépôt
        :param station: station à draîner
        :return: void
        """
        qsize = len(station.pods)
        if qsize < int(3 * station.capacity / 4):
            return
        pod = station.pods[0]
        if not pod.travelers:
            station.pods.remove(pod)
            pod.destination = self.get_random_free_shed()  # TODO : Prendre le dépôt le plus proche
            pod.priority = -1  # TODO : priorité à mettre à jour
            pod.travelers = None
            pod.source = station
            pod.position = 0
            pod.start_trip()  # TODO : le voyage d'une capsule
            print("Station %s : capsule draînée vers le dépôt %s" % (station.name, pod.destination.name))

    def fill_and_full_stations(self):
        """
        Appel le controleur pour completer la station. On considère que la station est en situation critique si il ne
        reste aucune capsule disponible. La demande est alors effectué avec une priorité maximale(1). La capsule vide
        sera donc autant prioritaire qu'une capsule pleine. Si il reste au moins une capsule alors la demande est
        effectué avec une priorité faible
        """
        for station in self.stations:
            if len(station.pods) <= max(1, int(station.capacity / 4)):
                # quasi vide --> station à compléter
                print("Station %s almost empty (caps_numb = %d)." % (station.name, len(station.pods)))
                if not station.pods:
                    self.refill(10, station)
                elif not station.capsule_arriving:
                    self.refill(6, station)
            if len(station.pods) >= min(station.capacity - 1, int(3 * station.capacity / 4)) and len(station.pods) > 1:
                # quasi pleine --> station à vider
                print("Station %s almost full (caps_numb = %d, waiting travelers = %d)." % (
                    station.name, station.estimated_capsules_number(), station.traveler_queue.qsize()))
                self.drain_pod_station(station)

    def refill(self, prio, destination):
        """
        Réapprovisionne une station qui en effectue la demande
        :param prio: Priorité de la demande (10 si critique) OBLIGATOIRE
        :param destination: Station qui effectue la demande OBLIGATOIRE
        """
        shed = random.choice(self.sheds)  # TODO : à remplacer par le dépôt le plus proche
        if prio == 10:
            test = False
            for pod in self.pods:
                if len(
                        pod.travelers) == 0 and pod.priority <= 6 and not pod.travelers:  # TODO: mémoriser les capsules vides
                    test = True
                    print("source:", type(pod.track), "||| destination:", destination.name)
                    trajet = shorter_way_tracks(pod.track, destination)
                    for i in range(len(trajet) - 1):
                        new_rules = []
                        change = trajet[i].beside.next == trajet[i + 1]
                        r = Rule(trajet[i].id, priority=10, empty=True, change=change)
                        new_rules.append(r)
                        self.send_list_rules(new_rules)
                if test:
                    break
            if test:
                if len(shed.pods) > 0:
                    drain_pod_shed(shed, destination, prio)
            else:
                if len(shed.pods) > 1:
                    drain_pod_shed(shed, destination, prio)
        else:
            if len(shed.pods) > 0:
                drain_pod_shed(shed, destination, prio)

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
                                route = s.next
                            else:
                                route = s.beside
                            for step in route.steps:
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

    def update(self):
        """
        Gestion du processus du réseau à chaque boucle d'événement simpy
        :return: void
        """
        while True:
            print("-------------------------------------------------------------")
            print("     Tick n°", self.env.now, " | Réseau :", self.name, "     ")
            print("-------------------------------------------------------------")
            if self._dynamic_routing and (self.env.now * self.env.sim_tick) % 30 == 0:
                # Toutes les 30 secondes on met à jour les tables de routage si l'option est activée
                yield from self._update_routing()
            while True:
                message = yield from self.read()
                if message is not None:
                    print(self.name, "  --  ", message["author"].name, "  --  ", message["type"])
                if message is None:
                    break
                elif "docked" == message["type"]:
                    # Une capsule stationne
                    pass
                elif "refill" == message["type"]:
                    # On demande à un dépôt d'envoyer une capsule à la station qui le demande
                    sheds = self.sheds
                    if sheds:
                        station = message["station"]
                        shed = choice(sheds)
                        yield from shed.write({
                            "author": self,
                            "type": "refill",
                            "station": station
                        })
                else:
                    raise ValueError("Invalid message")


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


def ascent_event(station, pod, _env, ascent_descent_duration, frequency):
    """
    Evénement de monter d'un voyageur dans une capsule
    :param station: station dans laquelle un voyageur monte dans une capsule
    :param pod: capsule dans laquelle un voyageur monte
    :param _env: environnement simpy de la simulation
    :param ascent_descent_duration: temps moyen de monté et descente d'un voyageur dans/depuis une capsule
    :param frequency: nombre de ticks par seconde
    :return: Fait remonter l'événement de monté d'un voyageur dans une capsule
    """
    ascent_timeout = _env.timeout(random_ascent_descent_duration(ascent_descent_duration, frequency))
    ascent_timeout.callbacks.append(lambda event: ascent_event_callback(station, pod))
    yield ascent_timeout


def random_ascent_descent_duration(ascent_descent_duration, frequency):
    """
    :return: A value between [|time-2, time+2|]. time is the defined duration (in the config file)
    for ascent and descent events.
    """
    random_seconds = random.randrange(ascent_descent_duration - 2, ascent_descent_duration + 2, 1)
    return random_seconds * frequency


def ascent_event_callback(station, pod):
    """
    Déclenche les fonctions qui modélisent la montée d'un voyageur dans une capsule
    C'est-à-dire le retrait de la capsule depuis la station dont elle part et le départ de la capsule
    :param station:
    :param pod:
    :return:
    """
    station.pods.remove(pod)
    pod.start_trip()  # TODO : départ d'une capsule


def update_weight(switch1, switch2, travel_time):
    """
    Met à jour le poids de la route reliant switch1 à switch2 qu'une capsule vient de parcourir
    S'ils ne sont pas reliés alors ne fait rien
    :param travel_time: temps mis par la capsule pour parcourir la route
    :param switch1: switch précédent la route empruntée par la capsule
    :param switch2: switch suivant la route empruntée par la capsule
    :return: boolean indiquant si il y a congestion
    """
    if switch1.next.next == switch2:
        route = switch1.next
    elif switch1.beside.next == switch2:
        route = switch1.beside
    else:
        return False
    route.weight = 0.875 * route.weight + 0.125 * travel_time
    return route.weight > 3 * route.expected_weight


def no_more_congestion(previous_switch, current_switch):
    """
    :param previous_switch: aiguillage précédent
    :param current_switch: aiguillage actuel
    :return: boolean étant true s'il n'y a plus de congestion sur la route entre les deux aiguillages et false sinon
    """
    if previous_switch.next.next == current_switch:
        route = previous_switch.next
    elif previous_switch.beside.next == current_switch:
        route = previous_switch.beside
    else:
        return True
    return route.weight < 2 * route.expected_weight


def disable_route(previous_switch, current_switch):
    """
    Rend impossible le passage par une route, ie met le poids de celle-ci à l'infini
    :param previous_switch: aiguillage de début de route
    :param current_switch: aiguillage de fin de route
    """
    if previous_switch.next.next == current_switch:
        route = previous_switch.next
    elif previous_switch.beside.next == current_switch:
        route = previous_switch.beside
    else:
        return
    route.weight = inf


def get_time_max(previous_switch, current_switch):
    """
    Retourne le temps à partir duquel on considère une route comme coupée. On prend comme limite
    10 * le temps de parcours en conditions normales
    :param previous_switch: aiguillage précédent la route
    :param current_switch: aiguillage suivant la route
    :return: temps à partir duquel on considère une route comme coupée
    """
    if previous_switch.next.next == current_switch:
        route = previous_switch.next
    elif previous_switch.beside.next == current_switch:
        route = previous_switch.beside
    else:
        return -1
    return 10 * route.expected_weight


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


def drain_pod_shed(shed, destination, prio):
    """
    Libère une capsule vide du dépôt
    La capsule est redirigée vers une station
    :param shed: le dépôt à draîner
    :param destination: la station à alimenter
    :return: void
    """
    qsize = len(shed.pods)
    if qsize == 0:
        print("Plus de capsules disponibles dans le dépôt", shed.name)
        return
    pod = shed.pods[0]
    if not pod.travelers:
        shed.pods.remove(pod)
        pod.destination = destination
        pod.priority = prio  # TODO : priorité à mettre à jour
        pod.travelers = None
        pod.source = shed
        pod.position = 0
        pod.start_trip()  # TODO
        print("Une capsule part du dépôt %s vers la station %s" % (shed.name, destination.name))


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
